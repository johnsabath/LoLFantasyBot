__author__ = 'John'

from fantasylcs import ALL_ROSTER_POSITIONS
from lolfantasybot import constants


def sort_players_by_role(player):
    player = player[0]
    if len(player.get_positions()) == 1:
        return ALL_ROSTER_POSITIONS.index(player.get_positions()[0])
    else:
        return len(ALL_ROSTER_POSITIONS)


def calculate_points(stats):
    points = 0

    for key in stats:
        if key in constants.POINTS_PER_STAT:
            points += constants.POINTS_PER_STAT[key] * stats[key]['actual']

    return points