#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This bot was written by Sam Reeves.  For all questions or comments
# please email me.  samtreeves@gmail.com

import tweepy
import time
import sys
import keys

# Do the OAuth dance... verify securely.  Declare verified user.
auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)
user = api.me()

# Follow everybody back
for follower in user.followers():
	follower.follow()

# Generate a list of friends
friends = []
for friend in user.friends():
	friends.append(friend.screen_name)

# Open the file of canned messages
argfile = str(sys.argv[1])
filename = open(argfile, 'r')
f = filename.readlines()
filename.close()

# Tweet a line every 60 seconds
for line in f:
	api.update_status(status=line)
	time.sleep(60)
