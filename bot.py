#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot was written by Sam Reeves.  For all questions or comments
# please email me.  samtreeves@gmail.com

import keys

import tweepy
import time
import random
import os.path
import dill

class dalek(object):
    "I am a twitter bot. Create an instance of me with bot = dalek()"

    def __init__(self):
        self.auth = tweepy.OAuthHandler(
                keys.consumer_key, keys.consumer_secret)
        self.auth.set_access_token(
                keys.access_token, keys.access_token_secret)

        self.api = tweepy.API(self.auth)

        if os.path.exists('followers'):
            with open('followers', 'rb') as infile:
                self.followers = dill.load(infile)
                
        if os.path.exists('friends'):
            with open('friends', 'rb') as infile:
                self.friends = dill.load(infile)
                
        if os.path.exists('DMs'):
            with open('DMs', 'rb') as infile:
                self.dms = dill.load(infile)
                self.most_recent_message = bot.getMessageID(self.dms[0])
                
        if os.path.exists('users'):
            with open('users', 'rb') as infile:
                self.users = dill.load(infile)
    
    def limit_handled(cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                time.sleep(15*60)

    def updateFollowers(self):
        for follower in tweepy.Cursor(self.api.followers).items():
            if follower not in self.followers:
                self.followers.append(follower)
        with open('followers', 'wb') as outfile:
            dill.dump(self.followers, outfile)

    def followEveryoneBack(self):
        for follower in self.followers:
            follower.follow()

    def updateFriends(self):
        for friend in tweepy.Cursor(self.api.friends).items():
            if friend not in self.friends:
                self.friends.append(friend)
        with open('followers', 'wb') as outfile:
            dill.dump(self.followers, outfile)

    def zombieTweet(self, interval=60, duration=1):
        lines = open('messages').read().splitlines()
        for i in range(duration):
            tweet = random.choice(lines)
            print(tweet)
            self.api.update_status(status=tweet)
            if duration > 1:
                time.sleep(interval*duration)

    def updateDMs(self):
        new_dm_call = self.api.list_direct_messages()

        if hasattr(self, 'dms'):
            if not self.most_recent_message == bot.getMessageID(new_dm_call[0]):
                unlogged_dms = []
                for item in new_dm_call:
                    if bot.getMessageID(item) > self.most_recent_message:
                        unlogged_dms.append(item)
                self.dms[:0] = unlogged_dms
        else:
            self.dms = new_dm_call
        self.most_recent_message = bot.getMessageID(self.dms[0])
        with open('DMs', 'wb') as outfile:
            dill.dump(self.dms, outfile)

    def addUser(self, user_id, admin_status=False):
        if not hasattr(self, 'users'):
            self.users = [[], []]
        self.users[0].append(user_id)

        if admin_status:
            self.users[1].append()

        with open('users', 'wb') as outfile:
            dill.dump(outfile, self.users)

    def subtractUser(self, user_id, wipe=False):
        if not hasattr(self, 'users'):
            return None

        elif user_id in self.users[1]:
            self.users[1].remove(user_id)
            if wipe:
                self.users[0].remove(user_id)
                with open('users', 'wb') as outfile:
                    dill.dump(self.users, outfile)

        elif user_id in self.users[0]:
            self.users[0].remove(user_id)
        with open('users', 'wb') as outfile:
            dill.dump(outfile, self.users)

    def getMessageID(self, message):
        return int(message.id)

    def getSenderID(self, message):
        senderID = message.message_create['sender_id']
        return int(senderID)

    def getHashtags(self, message):
        tags = []
        for tag in message.message_create['message_data']['entities']['hashtags']:
            tags.append(tag['text'])
        return tags
