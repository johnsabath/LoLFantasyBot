__author__ = 'John'

import re

POST_GAME_REGEX = re.compile("\[Spoilers?\] (.*) vs\.? (.*) / (\w{2}) LCS.* Week (\d*)")
PLAYER_TABLE_COLUMNS = ['Player', 'Points', '&nbsp;'*4, 'K^^[+2]', 'D^^[-0.5]', 'A^^[+1.5]', 'CS^^[+0.01]',
                        '&nbsp;'*4, '3x^^[+2]', '4x^^[+5]', '5x^^[+10]', 'K/A Bonus^^[+2]']
TEAM_TABLE_COLUMNS = ['Team', 'Points', '&nbsp;'*4, 'Win^^[+2]', 'Quick Win^^[+2]', 'First Blood^^[+2]', 'Towers^^[+1]', 'Dragons^^[+1]', 'Barons^^[+2]']

POINTS_PER_STAT = {
    'kills': 2,
    'deaths': -0.5,
    'assists': 1.5,
    'minionKills': 0.01,
    'doubleKills': 0,
    'tripleKills': 2,
    'quadraKills': 3,
    'pentaKills': 5,
    'killOrAssistBonus': 2,
    'firstBlood': 2,
    'towerKills': 1,
    'baronKills': 2,
    'dragonKills': 1,
    'matchVictory': 2,
    'matchDefeat': 0,
    'quickWinBonus': 2
}