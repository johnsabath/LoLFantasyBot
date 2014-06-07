'''
Created on May 29, 2014

@author: John Sabath
'''

import constants

def buildRedditTable(column_labels, grid):
    table = ""

    max_width = max([len(array) for array in grid])

    if len(column_labels) > max_width:
        max_width = len(column_labels)

    table += ("|" + (" {} |" * max_width) + "\n").format(*column_labels)
    table += "|" + (":-:|" * max_width) + "\n"

    for array in grid:
        table += "|"
        for label in column_labels:
            if "&nbsp;" not in label:
                table += " {}"
            table += " |"

        table = table.format(*array)
        table += "\n"

    return table

def correctTeamName(team_name):
    if team_name in constants.CORRECTION_DICT:
        return constants.CORRECTION_DICT[team_name]
    return team_name

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