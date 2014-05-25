'''
Created on May 21, 2014

@author: John
'''
import requests, json, collections

WEEK = "1"

positions = collections.OrderedDict()
positions["Top Lane"] = "Top"
positions["Jungler"] = "Jungle"
positions["Mid Lane"] = "Mid"
positions["AD Carry"] = "ADC"
positions["Support"] = "Support"

def calculatePlayerPoints(player_json, key):
    points = 0

    try:
        points += 2 * int(player_json['kills'][key])
        points += -0.5 * int(player_json['deaths'][key])
        points += 1.5 * int(player_json['assists'][key])

        points += 0.01 * int(player_json['minionKills'][key])

        points += 2 * int(player_json['tripleKills'][key])
        points += 5 * int(player_json['quadraKills'][key])
        points += 10 * int(player_json['pentaKills'][key])

        points += 2 * int(player_json['killOrAssistBonus'][key])
    except:
        pass

    return points

def calculateTeamPoints(team_json, key):
    points = 0

    try:
        points += 2 * int(team_json['firstBlood'][key])

        points += 2 * int(team_json['matchVictory'][key])

        points += 2 * int(team_json['baronKills'][key])
        points += 1 * int(team_json['towerKills'][key])
        points += 1 * int(team_json['dragonKills'][key])
    except:
        pass

    return points

if __name__ == '__main__':
    text = requests.get("http://fantasy.na.lolesports.com/en-US/api/season/4").text
    data = json.loads(text, object_pairs_hook=collections.OrderedDict)

    players = [data['proPlayers'][x] for x in data['proPlayers'] if calculatePlayerPoints(data['proPlayers'][x]['statsByWeek'][WEEK], "actualValue") != 0]
    teams = [data['proTeams'][x] for x in data['proTeams'] if calculateTeamPoints(data['proTeams'][x]['statsByWeek'][WEEK], "actualValue") != 0]


    green = "[{0:+.2f}](#green)"
    red = "[{0:+.2f}](#red)"

    players_by_projected_diff = sorted(players, key=lambda x:(calculatePlayerPoints(x['statsByWeek'][WEEK], "actualValue")-calculatePlayerPoints(x['statsByWeek'][WEEK], "projectedValue")), reverse=True)
    players_by_actual = sorted(players, key=lambda x:calculatePlayerPoints(x['statsByWeek'][WEEK], "actualValue"), reverse=True)
    teams_by_actual = sorted(teams, key=lambda x:calculateTeamPoints(x['statsByWeek'][WEEK], "actualValue"), reverse=True)

    print("| Player | Position | Points | Diff. from Projected |&nbsp;&nbsp;&nbsp;&nbsp;| K^^[+2] | D^^[-0.5] | A^^[+1.5] | CS^^[+0.01] |&nbsp;&nbsp;&nbsp;&nbsp;| Trips^^[+2] | Quads^^[+5] | Pents^^[+10]  | K/A Bonus^^[+2] |")
    print("|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|")

    for player in players_by_actual:
        stats = player['statsByWeek'][WEEK]
        actual = calculatePlayerPoints(stats, "actualValue")
        projected = calculatePlayerPoints(stats, "projectedValue")

        if (actual != 0):
            print("| [%s](http://lolesports.com/node/%s) | %s | %.2f | %s | | %s | %s | %s | %s | | %s | %s | %s | %s |" % (player['name'], player['riotId'], positions[player['positions'][0]], actual, green.format(actual-projected) if actual-projected >= 0 else red.format(actual-projected), stats['kills']['actualValue'], stats['deaths']['actualValue'], stats['assists']['actualValue'], stats['minionKills']['actualValue'], stats['tripleKills']['actualValue'], stats['quadraKills']['actualValue'], stats['pentaKills']['actualValue'], stats['killOrAssistBonus']['actualValue']))

    print()

    print("| Team | Points | Diff. from Projected |&nbsp;&nbsp;&nbsp;&nbsp;| Win^^[+2] | First Blood^^[+2] | Barons^^[+2] | Dragons^^[+1]| Towers^^[+1] |")
    print("|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|")

    for team in teams_by_actual:
        stats = team['statsByWeek'][WEEK]
        actual = calculateTeamPoints(stats, "actualValue")
        projected = calculateTeamPoints(stats, "projectedValue")
        if (actual != 0):
            print("| [%s](http://lolesports.com/node/%s) | %.2f | %s | | %s | %s | %s | %s | %s |" % (team['name'], team['riotId'], actual, green.format(actual-projected) if actual-projected >= 0 else red.format(actual-projected), stats['matchVictory']['actualValue'], stats['firstBlood']['actualValue'], stats['baronKills']['actualValue'], stats['dragonKills']['actualValue'], stats['towerKills']['actualValue']))

    print("&nbsp;\n\n**Extraordinary Performances (For better or for worse)**\n\n---")

    print("| Player | Points | Diff. from Projected |")
    print("|:-:|:-:|:-:|")

    for player in players_by_projected_diff[:5]:
        stats = player['statsByWeek'][WEEK]
        actual = calculatePlayerPoints(stats, "actualValue")
        projected = calculatePlayerPoints(stats, "projectedValue")
        print("| [%s](http://lolesports.com/node/%s) | %.2f | %s |" % (player['name'], player['riotId'], actual, green.format(actual-projected) if actual-projected >= 0 else red.format(actual-projected)))

    print("| ... | ... | ... |")

    for player in players_by_projected_diff[-5:]:
        stats = player['statsByWeek'][WEEK]
        actual = calculatePlayerPoints(stats, "actualValue")
        projected = calculatePlayerPoints(stats, "projectedValue")
        print("| [%s](http://lolesports.com/node/%s) | %.2f | %s |" % (player['name'], player['riotId'], actual, green.format(actual-projected) if actual-projected >= 0 else red.format(actual-projected)))
    '''
    print("&nbsp;\n\n**Best Performances per Role**\n\n---")

    for position in positions.keys():
        print("%s\n\n" % position)
        print("| Player | Points |")
        print("|:-:|:-:|")
        for player in [x for x in players_by_actual if x['positions'][0] == position]:
            actual = calculatePlayerPoints(player['statsByWeek'][WEEK], "actualValue")
            print("| [%s](http://lolesports.com/node/%s) | %+.2f |" % (player['name'], player['riotId'], actual))
        print("\n")
    '''