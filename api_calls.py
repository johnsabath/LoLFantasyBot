'''
Created on May 29, 2014

@author: John Sabath
'''
import datetime, requests, constants, collections, json, time

def getProgramming():
    now = datetime.datetime.now()
    text = requests.get(constants.PROGRAMMING_QUERY % (now.strftime("%Y-%m-%d"))).text

    return json.loads(text, object_pairs_hook=collections.OrderedDict)

def getFantasyPoints(tourney_id):
    text = requests.get(constants.FANTASY_GAMES_IN_PERIOD % (tourney_id, int(time.time()-30*60*60), int(time.time()))).text

    return json.loads(text, object_pairs_hook=collections.OrderedDict)

#
# TODO: Actually request this from the API again, except only do it once on
# start-up.
#
def getTournamentId(region):
    if region.upper() == "NA":
        return 104
    elif region.upper() == "EU":
        return 102

    return 0