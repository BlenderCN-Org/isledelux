#!python3
# -*- coding: utf-8 -*-

# Standard modules.
import time
import sys
import os
import random
import traceback
import logging

# Dependencies.
import tweepy

# Logging stuff.
# I think this has to go BEFORE module imports.
# Look into fixing this.
logger = logging.getLogger("isledelux")

streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt='%(asctime)s %(name)s: %(message)s',
    datefmt='%H:%M'
)

streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)
logger.setLevel(logging.INFO)

# Internal modules.
from config import *
import picture_handler
import render_image

# If this is False, skip the API call that sends the tweet.
run_live = True

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# Counters to store amount of minutes and number of tweets
total_tweet_time = 0
number_of_tweets = 0

while True:
    # Keep trying to tweet until we've tweeted something.
    tweeted = False
    i = 0

    while not tweeted:
        # Get the path to an image from the handler.
        image_path = picture_handler.fetch_image()

        if not image_path:
            render_image.render()
            image_path = picture_handler.fetch_image()

        try:
            logger.info("Tweeting image {}".format(image_path))
            if run_live:
                api.update_with_media(filename=image_path)
                picture_handler.cleanup_image(image_path)

            tweeted = True

        # Oh gosh, I am not a smart man. How do I into exceptions?
        except ConnectionAbortedError as e:
            print(e)
            print(e, file=open("error_log.txt", "a+"))

        # We could feed a family of six with all this spaghetti.
        except tweepy.error.TweepError as e:
            print(e.api_code)

            if e.api_code == 187:
                # Duplicate tweet. Get rid of the image and start over.
                logger.warning("Duplicate tweet!")
                picture_handler.cleanup_image(image_path)
                tweeted = False

            else:
                print(
                    "\r\n" + time.strftime("%H:%M:%S"),
                    file=open("error_log.txt", "a+")
                )

                traceback.print_exc(file=sys.stdout)
                traceback.print_exc(file=open("error_log.txt", "a+"))

                tweeted = False
                logger.warning("Trying again in 5 minutes...")
                time.sleep(300)

    # Pick a sort of random time to wait.
    sleepytime = random.randint(17000, 19000)  # 18000 seconds = 5 hours.

    logger.info("Sleeping for " + str(int(sleepytime / 60)) + " minutes...")

    total_tweet_time += (sleepytime / 60)
    number_of_tweets += 1
    average_tweet_time = int(total_tweet_time / number_of_tweets)

    logger.info("Average tweet time: {} minutes.".format(average_tweet_time))

    # Wait for the sort of random amount of time
    time.sleep(sleepytime)
