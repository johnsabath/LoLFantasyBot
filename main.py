'''
Created on May 21, 2014

@author: John Sabath - /u/_Zaga_
'''

import praw, configparser, datetime
import time, logging, pickle, os
import constants, api_calls, utility

# Initial values (these will be overwritten from the save file)
last_match_NA = 2530
last_match_EU = 2312

# Config file values
config = None

# JSON objects
programming_json = None
fantasy_json = None

# Duration that the main loop should sleep on this iteration
sleep_duration = 60

def buildTeamTable(team1, team2):
    table = []

    for team in (team1, team2):
        name = team['teamName']
        teamId = team['teamId']
        profile = "[%s](http://lolesports.com/node/%s)" % (name, teamId)
        barons = team['baronsKilled']
        dragons = team['dragonsKilled']
        towers = team['towersKilled']
        victory = 'X' if team['matchVictory'] == 1 else ''
        first_blood = 'X' if team['firstBlood'] == 1 else ''
        points = utility.calculateTeamPoints(team)

        table.append([profile, points, victory, first_blood, barons, dragons, towers])

    return utility.buildRedditTable(constants.TEAM_TABLE_COLUMNS, table)

def buildPlayerTable(game):
    table = []

    players = [key for key in fantasy_json['playerStats'][game] if "player" in key]

    for i, player_id in enumerate(players):
        player = fantasy_json['playerStats'][game][player_id]

        name = player['playerName']
        playerId = player['playerId']
        profile = "[%s](http://lolesports.com/node/%s)" % (name, playerId)
        points = utility.calculatePlayerPoints(player)
        kills = player['kills']
        deaths = player['deaths']
        assists = player['assists']
        cs = player['minionKills']
        trips = player['tripleKills'] if player['tripleKills'] > 0 else ''
        quads = player['quadraKills'] if player['quadraKills'] > 0 else ''
        pents = player['pentaKills'] if player['pentaKills'] > 0 else ''
        bonus = 'X' if (player['kills'] >= 10 or player['assists'] >= 10) else ''

        table.append([profile, "%.2f" % points, kills, deaths, assists, cs, trips, quads, pents, bonus])

        if i == 4:
            table.append(["|&nbsp;|"]*10)

    return utility.buildRedditTable(constants.PLAYER_TABLE_COLUMNS, table)

def createPostMatchThread(block, match, post):
    global last_match_NA
    global last_match_EU

    if post != "":
        title = "[Spoiler] %s / %s / Fantasy Discussion" % (match['matchName'], block['label'])
        logging.info(title)
        logging.info("-"*25)
        logging.info(post)

        r.submit("fantasylcs", title, post)

        if block['tournamentId'] == str(api_calls.getTournamentId("NA")):
            last_match_NA = int(match['matchId'])
        else:
            last_match_EU = int(match['matchId'])

def checkSchedule(r):
    global fantasy_json
    global programming_json
    global sleep_duration

    matches_are_live = False
    programming_json = api_calls.getProgramming()

    for block in programming_json:
        block_date = datetime.datetime.strptime(block['dateTime'].split('T')[0], "%Y-%m-%d")
        now = datetime.datetime.now()

        if block_date.day == now.day and block_date.month == now.month:
            if block['tournamentId'] in (str(api_calls.getTournamentId("EU")), str(api_calls.getTournamentId("NA"))):
                fantasy_json = api_calls.getFantasyPoints(int(block['tournamentId']))

                logging.debug(block['label'])
                for match_id in block['matches']:
                    logging.debug(match_id)

                    match = block['matches'][match_id]

                    region = "EU" if block['tournamentId'] == str(api_calls.getTournamentId("EU")) else "NA"
                    team1_name = match['contestants']['blue']['name']
                    team2_name = match['contestants']['red']['name']

                    post = buildPost(region, team1_name, team2_name, True)

                    if post != "":
                        if block['tournamentId'] == str(api_calls.getTournamentId("NA")) and int(match['matchId']) <= last_match_NA:
                            continue
                        if block['tournamentId'] == str(api_calls.getTournamentId("EU")) and int(match['matchId']) <= last_match_EU:
                            continue

                        createPostMatchThread(block, match, post)

                    if match['isLive'] == True:
                        logging.info("[LIVE MATCH] %s" % match['matchName'])
                        matches_are_live = True

    if matches_are_live:
        sleep_duration =  1 * 60 #1 minute
    else:
        sleep_duration = 20 * 60 #20 minutes

def buildPost(region, team1_name, team2_name, own_thread):
    post = ""

    team1_name = utility.correctTeamName(team1_name)
    team2_name = utility.correctTeamName(team2_name)

    for game in fantasy_json['teamStats']:
        team1_id = ""
        team2_id = ""

        for key in fantasy_json['teamStats'][game]:
            if "team" in key:
                if team1_id == "":
                    team1_id = key
                else:
                    team2_id = key

        game_teams = (fantasy_json['teamStats'][game][team1_id]['teamName'].lower(), fantasy_json['teamStats'][game][team2_id]['teamName'].lower())

        #logging.debug((team1_name.lower(), team2_name.lower()))
        #logging.debug(game_teams)
        #logging.debug("---")

        if team1_name.lower() in game_teams and team2_name.lower() in game_teams:
            if not own_thread:
                post += "^For ^in-depth ^fantasy ^discussions, ^visit ^/r/FantasyLCS\n\n"
                post += "###Fantasy Impact\n"
                post += "---\n"

            post += buildTeamTable(fantasy_json['teamStats'][game][team1_id], fantasy_json['teamStats'][game][team2_id])

            post += "&nbsp;\n\n"

            post += buildPlayerTable(game)

            post += "\n---\n"
            post += "^^The ^^API ^^that ^^this ^^bot ^^uses ^^is ^^extremely ^^finicky ^^\(rito ^^plz), ^^occasionally " \
                    "^^the ^^bot ^^will ^^post ^^incomplete ^^data ^^or ^^fail ^^to ^^post ^^completely.  \n"
            post += "^^I ^^am ^^maintained ^^by ^^/u/_Zaga_.  ^^To ^^learn ^^more ^^about ^^fantasy ^^LoL ^^visit ^^the " \
                    "^^official ^^fantasy ^^LoL ^^website ^^[here](http://fantasy.lolesports.com).  \n"
            post += "^^The ^^source ^^code ^^for ^^/u/LoLFantasyBot ^^can ^^be ^^found ^^[here](https://github.com/0Zaga0/LoLFantasyBot)."

            break

    return post

if __name__ == '__main__':
    global fantasy_json

    cached_threads = []

    logging.basicConfig(level=logging.DEBUG)

    config = configparser.ConfigParser()
    config.read("config.cfg")

    if (os.path.isfile("last_processed_game.dat")):
        f = open("last_processed_game.dat", "rb")
        data = pickle.load(f)
        last_match_NA = data[0]
        last_match_EU = data[1]
        f.close()

    r = praw.Reddit(user_agent="LoLFantasyBot created by /u/_Zaga_")
    r.login(config.get("Login Info", "username"), config.get("Login Info", "password"))

    while True:
        logging.info((last_match_NA, last_match_EU))

        try:
            checkSchedule(r)
        except Exception as ex:
            logging.exception("Failed in checkSchedule()")

        try:
            subreddit = r.get_subreddit('leagueoflegends')

            for submission in subreddit.get_new(limit=100):
                title_search = constants.POST_GAME_REGEX.search(submission.title)

                if submission.id not in cached_threads and title_search:
                    team1  = title_search.groups()[0]
                    team2  = title_search.groups()[1]
                    region = title_search.groups()[2]
                    week   = title_search.groups()[3]

                    fantasy_json = api_calls.getFantasyPoints(api_calls.getTournamentId(region))

                    logging.info(("|"+(" %s |"*4))%(region, week, team1, team2))

                    post = buildPost(region, team1, team2, False)

                    logging.debug(post)

                    if post != "":
                        cached_threads.append(submission.id)
                        submission.add_comment(post)

        except Exception as ex:
            logging.exception("Failed to find game/post comment")

        f = open("last_processed_game.dat", "wb")
        pickle.dump((last_match_NA, last_match_EU), f)
        f.close()

        logging.info("Sleeping for %s minute(s)" % (sleep_duration/60))
        time.sleep(sleep_duration)