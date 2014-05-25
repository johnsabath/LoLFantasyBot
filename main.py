'''
Created on May 21, 2014

@author: John Sabath - /u/_Zaga_
'''

import praw, configparser, requests, collections, json, re, time, os, sys

FANTASY_API_URL = "http://na.lolesports.com:80/api/gameStatsFantasy.json?tournamentId=%s"
FANTASY_API_URL_WITH_TIME = "http://na.lolesports.com:80/api/gameStatsFantasy.json?tournamentId=%s&dateBegin=%s&dateEnd=%s"
LEAGUE_API_URL = "http://na.lolesports.com:80/api/league/%s.json"

POST_GAME_REGEX = re.compile("\[Spoilers?\] (.*) vs\.? (.*) / (\w{2}) LCS.* Week (\d*)")

CORRECTION_DICT = {
    'Gambit':'Gambit Gaming',
    'Cloud 9':'Cloud 9 ',
    'Complexity':'Complexity ',
    'Dignitas':'Team Dignitas',
    'Evil Genius':'Evil Geniuses'
}

def getDefaultTournamentId(region):

    if region.upper() == "NA":
        return 104
    elif region.upper() == "EU":
        return 102

    return 0

def generatePostText(region, week, team1_name, team2_name):
    if team1_name in CORRECTION_DICT:
        team1_name = CORRECTION_DICT[team1_name]

    if team2_name in CORRECTION_DICT:
        team2_name = CORRECTION_DICT[team2_name]

    post = ""

    text = requests.get(FANTASY_API_URL_WITH_TIME % (getDefaultTournamentId(region), int(time.time()-30*60*60), int(time.time()))).text
    data = json.loads(text, object_pairs_hook=collections.OrderedDict)

    for game in data['teamStats']:
        team1_id = ""
        team2_id = ""

        players = [key for key in data['playerStats'][game] if "player" in key]

        for key in data['teamStats'][game]:
            if "team" in key:
                if team1_id == "":
                    team1_id = key
                else:
                    team2_id = key

        #print("%s = %s?" %(data['teamStats'][game][team1_id]['teamName'].lower(), team1_name.lower()))
        #print("%s = %s?" %(data['teamStats'][game][team2_id]['teamName'].lower(), team2_name.lower()))

        if (data['teamStats'][game][team1_id]['teamName'].lower() == team1_name.lower() \
                and data['teamStats'][game][team2_id]['teamName'].lower() == team2_name.lower()) \
            or (data['teamStats'][game][team2_id]['teamName'].lower() == team1_name.lower() \
                and data['teamStats'][game][team1_id]['teamName'].lower() == team2_name.lower()):
            #Game Found
            #fantasy_data = getLoLFantasyJSON()

            team1 = data['teamStats'][game][team1_id]
            team2 = data['teamStats'][game][team2_id]

            post += "^For ^in-depth ^fantasy ^discussions, ^visit ^/r/FantasyLCS\n\n"
            post += "###Fantasy Impact\n"
            post += "---\n"
            post += "| Team | Points |&nbsp;&nbsp;&nbsp;&nbsp;| Win^^[+2] | First Blood^^[+2] | Barons^^[+2] | Dragons^^[+1]| Towers^^[+1] |\n"
            post += "|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"
            post += "|[%s](http://lolesports.com/node/%s)| %+.2f | | %s | %s | %s | %s | %s |\n" % (team1['teamName'], team1['teamId'], getTeamPoints(team1), 'X' if team1['matchVictory'] == 1 else '', 'X' if team1['firstBlood'] == 1 else '', team1['baronsKilled'], team1['dragonsKilled'], team1['towersKilled'])
            post += "|[%s](http://lolesports.com/node/%s)| %+.2f | | %s | %s | %s | %s | %s |\n" % (team2['teamName'], team2['teamId'], getTeamPoints(team2), 'X' if team2['matchVictory'] == 1 else '', 'X' if team2['firstBlood'] == 1 else '', team2['baronsKilled'], team2['dragonsKilled'], team2['towersKilled'])
            post += "&nbsp;\n\n"
            post += "| Player | Points |&nbsp;&nbsp;&nbsp;&nbsp;| K^^[+2] | D^^[-0.5] | A^^[+1.5] | CS^^[+0.01] |&nbsp;&nbsp;&nbsp;&nbsp;| Trips^^[+2] | Quads^^[+5] | Pents^^[+10]  | K/A Bonus^^[+2] |\n"
            post += "|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

            for player_id in players[:5]:
                player = data['playerStats'][game][player_id]
                post += "|[%s](http://lolesports.com/node/%s)| %+.2f | | %s | %s | %s | %s | | %s | %s | %s | %s |\n" % (player['playerName'], player['playerId'], getPlayerPoints(player), player['kills'], player['deaths'], player['assists'], player['minionKills'], player['tripleKills'] if player['tripleKills'] > 0 else '', player['quadraKills'] if player['quadraKills'] > 0 else '', player['pentaKills'] if player['pentaKills'] > 0 else '', 'X' if (player['kills'] >= 10 or player['assists'] >= 10) else '')

            post += "|&nbsp;|\n"

            for player_id in players[5:]:
                player = data['playerStats'][game][player_id]
                post += "|[%s](http://lolesports.com/node/%s)| %+.2f | | %s | %s | %s | %s | | %s | %s | %s | %s |\n" % (player['playerName'], player['playerId'], getPlayerPoints(player), player['kills'], player['deaths'], player['assists'], player['minionKills'], player['tripleKills'] if player['tripleKills'] > 0 else '', player['quadraKills'] if player['quadraKills'] > 0 else '', player['pentaKills'] if player['pentaKills'] > 0 else '', 'X' if (player['kills'] >= 10 or player['assists'] >= 10) else '')

            post += "\n---\n"
            post += "^^I ^^am ^^maintained ^^by ^^/u/_Zaga_.  ^^To ^^learn ^^more ^^about ^^fantasy ^^LoL ^^visit ^^the ^^official ^^fantasy ^^LoL ^^website ^^[here](http://fantasy.lolesports.com).  \n"
            post += "^^The ^^API ^^that ^^this ^^bot ^^uses ^^is ^^extremely ^^finicky ^^\(rito ^^plz), ^^occasionally ^^the ^^bot ^^will ^^post ^^incomplete ^^data ^^or ^^fail ^^to ^^post ^^completely."

    return post

def getTeamPoints(team_json):
    points = 0

    if int(team_json['firstBlood']) == 1:
        points += 2

    if int(team_json['matchVictory']) == 1:
        points += 2

    points += 2 * int(team_json['baronsKilled'])
    points += 1 * int(team_json['towersKilled'])
    points += 1 * int(team_json['dragonsKilled'])

    return points

def getPlayerPoints(player_json):
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

def getLoLFantasyJSON():
    text = requests.get("http://fantasy.na.lolesports.com/en-US/api/season/4").text
    return json.loads(text, object_pairs_hook=collections.OrderedDict)

if __name__ == '__main__':
    cached_threads = []
    username = ""
    password = ""

    looping = True

    if "--cron" in sys.argv:
        looping = False

    if os.path.isfile("config.cfg"):
        config = configparser.ConfigParser()
        config.read("config.cfg")
        username = config.get("Login Info", "username")
        password = config.get("Login Info", "password")
    else:
        username = os.environ['REDDIT_USERNAME']
        password = os.environ['REDDIT_PASSWORD']

    r = praw.Reddit(user_agent="LoLFantasyBot created by /u/_Zaga_")
    r.login(username, password)

    while True:
        try:
            subreddit = r.get_subreddit('leagueoflegends+fantasylcs')
            for submission in subreddit.get_new(limit=200):
                title_search = POST_GAME_REGEX.search(submission.title)

                if submission.id not in cached_threads and title_search:
                    #WE'VE FOUND A THREAD
                    team1 = title_search.groups()[0]
                    team2 = title_search.groups()[1]
                    region = title_search.groups()[2]
                    week = title_search.groups()[3]

                    print(region, week, team1, team2, sep=" | ")

                    post = generatePostText(region, week, team1, team2)
                    print(post)

                    if post != "":
                        cached_threads.append(submission.id)
                        submission.add_comment(post)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        if not looping:
            break

        time.sleep(60)