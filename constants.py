'''
Created on May 29, 2014

@author: John Sabath
'''
import re

# API URLS
PROGRAMMING_QUERY = "http://na.lolesports.com/api/programming.json/?parameters[method]=next&parameters[time]=%s&parameters[limit]=6&parameters[expand_matches]=1"
FANTASY_GAMES_IN_PERIOD = "http://na.lolesports.com:80/api/gameStatsFantasy.json?tournamentId=%s&dateBegin=%s&dateEnd=%s"
#GAME_QUERY = "http://na.lolesports.com:80/api/game/%s.json"
#LEAGUE_QUERY = "http://na.lolesports.com:80/api/league/%s.json"
#CHAMP_INFO_QUERY = "https://prod.api.pvp.net/api/lol/static-data/na/v1.2/champion/%s?champData=info&api_key=%s"

# TABLE COLUMNS
PLAYER_TABLE_COLUMNS = [ 'Player', 'Points', '&nbsp;'*4, 'K^^[+2]', 'D^^[-0.5]', 'A^^[+1.5]', 'CS^^[+0.01]',
                         '&nbsp;'*4, 'Trips^^[+2]', 'Quads^^[+5]', 'Pents^^[+10]', 'K/A Bonus^^[+2]' ]
TEAM_TABLE_COLUMNS = [ 'Team', 'Points', '&nbsp;'*4, 'Win^^[+2]', 'First Blood^^[+2]', 'Barons^^[+2]', 'Dragons^^[+1]', 'Towers^^[+1]' ]

# TITLE FORMAT FOR FINDING POST-MATCH THREADS
POST_GAME_REGEX = re.compile("\[Spoilers?\] (.*) vs\.? (.*) / (\w{2}) LCS.* Week (\d*)")

# CORRECTION DICTIONARY FOR WHEN FULL TEAM NAMES AREN'T USED IN POST-MATCH TITLES,
# OR FOR WHEN RIOT HAS WEIRD TRAILING SPACES IN CERTAIN TEAM NAMES
CORRECTION_DICT = {
    'Gambit':'Gambit Gaming',
    'Cloud 9':'Cloud9 ',
    'Cloud9':'Cloud9 ',
    'Complexity':'Complexity ',
    'Dignitas':'Team Dignitas',
    'Evil Genius':'Evil Geniuses'
}