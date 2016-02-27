__author__ = 'John'

import pickle
import datetime
import time

from lolfantasybot import reddit
from fantasylcs import FantasyLCS

fantasylcs = FantasyLCS(season_id=12)
fantasylcs.load()

completed_matches = []

#
# Initialize completed matches list, so that we don't make duplicate threads
#
for match in fantasylcs.get_matches():
    utc_now = datetime.datetime.utcnow()

    if match.get_datetime().naive < utc_now - datetime.timedelta(days=1) and match.is_completed():
        completed_matches.append(match.get_id())

#
# Main loop
#
running = True
while running:
    try:
        fantasylcs.load()

        for match in fantasylcs.get_matches():
            if match.is_completed() and match.get_id() not in completed_matches:
                thread = reddit.create_own_thread(match, subreddit="fantasylcs")
                reddit.r.get_subreddit("fantasylcs").set_flair(thread, "Game Thread", "gamethread")
                completed_matches.append(match.get_id())
                print("Posted thread: %s" % thread)

        time.sleep(300)
    except Exception, e:
        print(e)
        time.sleep(60)


