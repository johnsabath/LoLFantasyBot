'''
Created on May 21, 2014

@author: John Sabath - /u/_Zaga_
'''

import praw, configparser, requests, collections
import json, re, time, logging

FANTASY_API_URL = "http://na.lolesports.com:80/api/gameStatsFantasy.json?tournamentId=%s"
FANTASY_API_URL_WITH_TIME = "http://na.lolesports.com:80/api/gameStatsFantasy.json?tournamentId=%s&dateBegin=%s&dateEnd=%s"
LEAGUE_API_URL = "http://na.lolesports.com:80/api/league/%s.json"

PLAYER_TABLE_HEADER = "| Player | Points |&nbsp;&nbsp;&nbsp;&nbsp;| K^^[+2] | D^^[-0.5] | A^^[+1.5] | CS^^[+0.01] |" \
                      "&nbsp;&nbsp;&nbsp;&nbsp;| Trips^^[+2] | Quads^^[+5] | Pents^^[+10]  | K/A Bonus^^[+2] |\n"
PLAYER_TABLE_VALUES = "|[%s](http://lolesports.com/node/%s)| %+.2f | | %s | %s | %s | %s | | %s | %s | %s | %s |\n"

TEAM_TABLE_HEADER = "| Team | Points |&nbsp;&nbsp;&nbsp;&nbsp;| Win^^[+2] | First Blood^^[+2] | Barons^^[+2] | Dragons^^[+1]| Towers^^[+1] |\n"
TEAM_TABLE_VALUES = "|[%s](http://lolesports.com/node/%s)| %+.2f | | %s | %s | %s | %s | %s |\n"

POST_GAME_REGEX = re.compile("\[Spoilers?\] (.*) vs\.? (.*) / (\w{2}) LCS.* Week (\d*)")

CORRECTION_DICT = {
    'Gambit':'Gambit Gaming',
    'Cloud 9':'Cloud 9 ',
    'Complexity':'Complexity ',
    'Dignitas':'Team Dignitas',
    'Evil Genius':'Evil Geniuses'
}

def calculateTeamPoints(team_json):
    points = 0

    if int(team_json['firstBlood']) == 1:
        points += 2

    if int(team_json['matchVictory']) == 1:
        points += 2

    points += 2 * int(team_json['baronsKilled'])
    points += 1 * int(team_json['towersKilled'])
    points += 1 * int(team_json['dragonsKilled'])

    return points

def calculatePlayerPoints(player_json):
    points = 0

    points += 2 * int(player_json['kills'])
    points += -0.5 * int(player_json['deaths'])
    points += 1.5 * int(player_json['assists'])

    points += 0.01 * int(player_json['minionKills'])

    points += 2 * int(player_json['tripleKills'])
    points += 5 * int(player_json['quadraKills'])
    points += 10 * int(player_json['pentaKills'])

    if int(player_json['assists']) >= 10 or int(player_json['kills']) >= 10:
        points += 2

    return points

def getTournamentId(region):

    if region.upper() == "NA":
        return 104
    elif region.upper() == "EU":
        return 102

    return 0

def buildTeamTable(team1, team2):
    post = ""

    post += TEAM_TABLE_HEADER
    post += "|" + (TEAM_TABLE_HEADER.count('|')-1)*":-:|" + "\n"

    for team in (team1, team2):
        name = team['teamName']
        teamId = team['teamId']
        barons = team['baronsKilled']
        dragons = team['dragonsKilled']
        towers = team['towersKilled']
        victory = 'X' if team['matchVictory'] == 1 else ''
        first_blood = 'X' if team['firstBlood'] == 1 else ''
        points = calculateTeamPoints(team)

        post += TEAM_TABLE_VALUES % (name, teamId, points, victory, first_blood, barons, dragons, towers)

    return post

def buildPlayerTable(game, full_json):
    post = ""
    players = [key for key in full_json['playerStats'][game] if "player" in key]

    post += PLAYER_TABLE_HEADER
    post += "|" + (PLAYER_TABLE_HEADER.count('|')-1)*":-:|" + "\n"

    for i, player_id in enumerate(players):
        player = full_json['playerStats'][game][player_id]

        name = player['playerName']
        playerId = player['playerId']
        points = calculatePlayerPoints(player)
        kills = player['kills']
        deaths = player['deaths']
        assists = player['assists']
        cs = player['minionKills']
        trips = player['tripleKills'] if player['tripleKills'] > 0 else ''
        quads = player['quadraKills'] if player['quadraKills'] > 0 else ''
        pents = player['pentaKills'] if player['pentaKills'] > 0 else ''
        bonus = 'X' if (player['kills'] >= 10 or player['assists'] >= 10) else ''

        post += PLAYER_TABLE_VALUES % (name, playerId, points, kills, deaths, assists, cs, trips, quads, pents, bonus)

        if i == 4:
            post += "|&nbsp;|\n"

    return post

def buildPost(region, week, team1_name, team2_name):
    if team1_name in CORRECTION_DICT:
        team1_name = CORRECTION_DICT[team1_name]

    if team2_name in CORRECTION_DICT:
        team2_name = CORRECTION_DICT[team2_name]

    post = ""

    text = requests.get(FANTASY_API_URL_WITH_TIME % (getTournamentId(region), int(time.time()-30*60*60), int(time.time()))).text
    full_json = json.loads(text, object_pairs_hook=collections.OrderedDict)

    for game in full_json['teamStats']:
        team1_id = ""
        team2_id = ""

        for key in full_json['teamStats'][game]:
            if "team" in key:
                if team1_id == "":
                    team1_id = key
                else:
                    team2_id = key

        game_teams = (full_json['teamStats'][game][team1_id]['teamName'].lower(), full_json['teamStats'][game][team2_id]['teamName'].lower())

        #logging.debug(game_teams)

        if team1_name.lower() in game_teams and team2_name.lower() in game_teams:
            post += "^For ^in-depth ^fantasy ^discussions, ^visit ^/r/FantasyLCS\n\n"
            post += "###Fantasy Impact\n"
            post += "---\n"

            post += buildTeamTable(full_json['teamStats'][game][team1_id], full_json['teamStats'][game][team2_id])

            post += "&nbsp;\n\n"

            post += buildPlayerTable(game, full_json)

            post += "\n---\n"
            post += "^^The ^^API ^^that ^^this ^^bot ^^uses ^^is ^^extremely ^^finicky ^^\(rito ^^plz), ^^occasionally " \
                    "^^the ^^bot ^^will ^^post ^^incomplete ^^full_json ^^or ^^fail ^^to ^^post ^^completely.  \n"
            post += "^^I ^^am ^^maintained ^^by ^^/u/_Zaga_.  ^^To ^^learn ^^more ^^about ^^fantasy ^^LoL ^^visit ^^the " \
                    "^^official ^^fantasy ^^LoL ^^website ^^[here](http://fantasy.lolesports.com).  \n"
            post += "^^The ^^source ^^code ^^for ^^/u/LoLFantasyBot ^^can ^^be ^^found ^^[here](https://github.com/0Zaga0/LoLFantasyBot)."

            break

    return post

if __name__ == '__main__':
    cached_threads = []

    logging.basicConfig(level=logging.DEBUG)

    config = configparser.ConfigParser()
    config.read("config.cfg")

    r = praw.Reddit(user_agent="LoLFantasyBot created by /u/_Zaga_")
    r.login(config.get("Login Info", "username"), config.get("Login Info", "password"))

    while True:
        try:
            subreddit = r.get_subreddit('leagueoflegends+fantasylcs')
            for submission in subreddit.get_new(limit=100):
                title_search = POST_GAME_REGEX.search(submission.title)

                if submission.id not in cached_threads and title_search:
                    team1 = title_search.groups()[0]
                    team2 = title_search.groups()[1]
                    region = title_search.groups()[2]
                    week = title_search.groups()[3]

                    logging.info(("|"+(" %s |"*4))%(region, week, team1, team2))

                    post = buildPost(region, week, team1, team2)
                    logging.debug(post)

                    if post != "":
                        cached_threads.append(submission.id)
                        submission.add_comment(post)

        except Exception as ex:
            logging.exception("YOU DONE MESSED UP, A-A-RON")

        time.sleep(60)