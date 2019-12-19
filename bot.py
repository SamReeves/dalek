#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This bot was written by Sam Reeves.  For all questions or comments
# please email me.  samtreeves@gmail.com

import tweepy
import time
import sys
import keys

auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

argfile = str(sys.argv[1])
filename = open(argfile, 'r')
f = filename.readlines()
filename.close()

for line in f:
	api.update_status(status=line)
	time.sleep(180)
