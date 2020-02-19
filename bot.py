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
        if os.path.exists('local_cache.pkl'):
            f = open("local_cache.pkl", "rb")
            self.cache = dill.load(f)
        else:
            self.cache = {}

    def limit_handled(cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                time.sleep(15*60)
                
    def writeCache(self):
        f = open("local_cache.pkl", "wb")
        dill.dump(self.cache, f)
        f.close()
        
    def updateFollowers(self):
        for follower in tweepy.Cursor(self.api.followers).items():
            if follower.id not in self.cache['followers']:
                self.cache['followers'].append(follower.id)

    def followEveryoneBack(self):
        for follower_id in self.cache['followers']:
            if follower_id not in self.cache['friends']:
                self.api.follow(follower_id)

    def updateFriends(self):
        for friend in tweepy.Cursor(self.api.friends).items():
            if friend.id not in self.cache['friends']:
                self.cache['friends'].append(friend.id)

    def zombieTweet(self, interval=60, duration=1):
        # tweet a random status from cache['statuses']
        for i in range(duration):
            tweet = random.choice(self.cache['statuses'])
            print(tweet)
            self.api.update_status(status=tweet)
            if duration > 1:
                time.sleep(interval*duration)

    def updateDMs(self):
        # do a call for new dms
        new_dm_call = self.api.list_direct_messages()
        
        # if no cache exists, create one
        if 'dm_cache' not in self.cache:
            for dm in new_dm_call:
                self.cache['dm_cache'][0][0] = dm.id
                self.cache['dm_cache'][0][1] = dm

        # if cache exists, update with unique data
        elif self.cache['dm_cache'][0][0] < new_dm_call[0].id:
            for dm in new_dm_call:
                if self.cache['dm_cache'][0][0] < dm.id:
                    self.cache['dm_cache'][0][0] = dm.id
    
    def addUser(self, user_id, admin_status=False):
        # if users not cached, create empty list
        if 'users' not in self.cache:
            self.cache['users'] = {'user' : [], 'admin' : []}
            
        # add user
        self.cache['users']['user'].append(user_id)
        
        # add admin rights
        if admin_status:
            self.cache['users']['admin'].append()
            
        # remove duplicates
        self.cache['users']['user'] = set(self.cache['users']['user'])
        self.cache['users']['admin'] = set(self.cache['users']['admin'])

    def removeUser(self, user_id, wipe=False):
        
        # if users not cached, create empty list
        if 'users' not in self.cache:
            self.cache['users'] = [[], []]
        
        #if user is admin, remove admin
        if user_id in self.cache['users'][1]:
            self.cache['users'][1].remove(user_id)
        
        #also remove admin from users
            if wipe:
                self.cache['users'][0].remove(user_id)
        
        #remove non-admin user
        elif user_id in self.cache['users'][0]:
            self.cache['users'][0].remove(user_id)

    def returnHashtags(message):
        tags = []
        for tag in message.message_create['message_data']['entities']['hashtags']:
            tags.append(tag['text'])
        return tags

    def addStatus(status):
        self.cache['statuses'].append(status)

    def groupConversations(self):
        # if no hash exists, create one
        if 'conversations' not in self.cache:
            self.cache['conversations'] = {}
            
        # check every cached message to see if it is in a conversation
        for message_id in self.cache['dm_cache'].keys():
            user_id = int(self.cache['dm_cache'][message_id].message_create['sender_id'])
            
            # begin a conversation
            if user_id not in self.cache['conversations'].keys():
                self.cache['conversations'][user_id] = []

            # continue a conversation
            if message_id not in self.cache['conversations'].values():
                self.cache['conversations'][user_id].append(message_id)
                
    def respond(self):
        # respond to each conversation with appropriate message
        for user_id in self.cache['conversations']:
            if user_id in self.cache['users']['admin']:
                message = "Greetings, Admin.  I have acknowledged your message."
            elif user_id in self.cache['users']['user']:
                message = "Greetings, User.  I have acknowledged your message."
            else:
                message = "You are an unrecognized user.  Please contact an Admin for access."
            self.api.send_direct_message(user_id, message)
            
        # delete the conversations from the cache leaving the most recent
        self.cache['dm_cache'] = {max(bot.cache['dm_cache']) : bot.cache['dm_cache'][max(bot.cache['dm_cache'])]}
                
        # delete the conversatoin
        del self.cache['conversations'][user_id]