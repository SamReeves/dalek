#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot was written by Sam Reeves.  For all questions or comments
# please email me.  samtreeves@gmail.com

import tweepy
import time
import sys
import keys

class dalek:
    "I am a twitter bot."

    def authenticateUser():
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)

        api = tweepy.API(auth)
        user = api.me()
        return api, user


    def knowFollowers():
        followers = []
        for follower in user.followers():
            followers.append(follower)
        return followers


    def followEveryoneBack():
        for follower in followers:
	    follower.follow()


    def knowFriends():
        friends = []
        for friend in user.friends():
	    friends.append(friend.screen_name)
        return friends


    def openResource(resource):
        filename = open(resource, 'r')
        content = filename.readlines()
        filename.close()
        return content

    def zombieTweet(resource, interval=60)
        for line in resource:
	    api.update_status(status=line)
	    time.sleep(interval)



