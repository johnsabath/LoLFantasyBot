__author__ = 'John'

import praw
import configparser
import os

from lolfantasybot import constants, utility


username = None
password = None

if os.path.exists("config.cfg"):
    config = configparser.ConfigParser()
    config.read("config.cfg")
    username = config.get("Login Info", "username")
    password = config.get("Login Info", "password")
else:
    username = os.environ.get('REDDIT_USERNAME')
    password = os.environ.get('REDDIT_PASSWORD')

if username is None or password is None:
    print("Critical Error: Username or Password not set")
    exit()


r = praw.Reddit(user_agent="LoLFantasyBot created by /u/_Zaga_")
r.login(username, password)


def get_new_postgame_threads(subreddit="leagueoflegends"):
    threads = r.get_subreddit(subreddit).get_new(limit=50)
    out = []

    for thread in threads:
        title_regex = constants.POST_GAME_REGEX.match(thread.title)
        if title_regex:
            out.append((title_regex.group(1), title_regex.group(2), thread))

    return out


def _generate_post_content(match, own_thread=False):
    blue_team = match.get_blue_team()
    red_team = match.get_red_team()

    blue_team_players = sorted(match.get_player_stats(blue_team.get_id()), key=utility.sort_players_by_role)
    red_team_players = sorted(match.get_player_stats(red_team.get_id()), key=utility.sort_players_by_role)

    blue_team_stats = blue_team.get_single_match_stats(match.get_id())
    red_team_stats = red_team.get_single_match_stats(match.get_id())

    teams = []
    players = []

    for team, stats in [(blue_team, blue_team_stats), (red_team, red_team_stats)]:
        points = utility.calculate_points(stats)
        teams.append([
            team.get_name(),
            "%.2f" % points,
            "X" if stats['matchVictory']['actual'] else "",
            "X" if stats['quickWinBonus']['actual'] else "",
            "X" if stats['firstBlood']['actual'] else "",
            stats['towerKills']['actual'],
            stats['dragonKills']['actual'],
            stats['baronKills']['actual']
        ])

    for player_stats in [blue_team_players, None, red_team_players]:
        if player_stats is None:
            players.append([""] * 12)
            continue

        for player, stats in player_stats:
            points = utility.calculate_points(stats)

            pentas = stats['pentaKills']['actual']
            quadras = stats['quadraKills']['actual'] - pentas
            triples = stats['tripleKills']['actual'] - quadras

            players.append([
                player.get_name(),
                "%.2f" % points,
                stats['kills']['actual'],
                stats['deaths']['actual'],
                stats['assists']['actual'],
                stats['minionKills']['actual'],
                triples,
                quadras,
                pentas,
                "X" if stats['killOrAssistBonus']['actual'] else "",
            ])

    post = "###Official Fantasy Points\n"
    post += "---\n"
    post += "Completed in %d:%02d\n\n" % (red_team_stats['secondsPlayed']['actual'] / 60,
                                          red_team_stats['secondsPlayed']['actual'] % 60)
    post += build_markdown_table(constants.TEAM_TABLE_COLUMNS, teams)
    post += "\n\n"
    post += build_markdown_table(constants.PLAYER_TABLE_COLUMNS, players)
    post += "\n---\n"
    post += "^^LoLFantasyBot ^^is ^^a ^^free ^^service ^^provided ^^by ^^http://FantasyRift.com ^^and ^^/u/_Zaga_.  " \
            "^^To ^^learn ^^more ^^about ^^FantasyLCS ^^visit ^^the ^^official ^^FantasyLCS ^^website " \
            "^^[here](http://fantasy.lolesports.com)"

    return post


def create_own_thread(match, subreddit="fantasylcs"):
    title = "[Spoiler] %s vs %s / %s Week %s / Fantasy Discussion" % (match.get_blue_team().get_name(),
                                                                      match.get_red_team().get_name(),
                                                                      match.get_blue_team().get_league(),
                                                                      match.get_week())
    post = _generate_post_content(match, own_thread=True)

    return r.submit(subreddit, title, post)


def build_markdown_table(column_labels, grid):
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