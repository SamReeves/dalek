#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot was written by Sam Reeves.  For all questions or comments
# please email me.  samtreeves@gmail.com

import keys

import tweepy
import time
import os.path
import dill
import random


class dalek(object):
    "I am the basic i/o of a twitter bot."

    def __init__(self):
        self.auth = tweepy.OAuthHandler(
                keys.consumer_key, keys.consumer_secret)
        self.auth.set_access_token(
                keys.access_token, keys.access_token_secret)

        self.api = tweepy.API(self.auth)
        if os.path.exists('cache.pkl'):
            f = open('cache.pkl', 'rb')
            self.cache = dill.load(f)
            f.close()
        else:
            self.dm_cache = {}
        if os.path.exists('dm_cache.pkl'):
            g = open('dm_cache.pkl', 'rb')
            self.cache = dill.load(g)
            g.close()
        else:
            self.cache = {}

    def limitHandled(cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                time.sleep(15*60)

    def writeCache(self):
        f = open('cache.pkl', 'wb')
        dill.dump(self.cache, f)
        f.close()
        g = open('dm_cache.pkl', 'wb')
        dill.dump(self.dm_cache, g)
        g.close()
        h = open('users.pkl', 'wb')
        dill.dump(self.users, h)
        h.close()

    def updateFollowers(self):
        for follower in tweepy.Cursor(self.api.followers).items():
            if follower.id not in self.cache['followers']:
                self.cache['followers'].append(follower.id)

    def updateFriends(self):
        for friend in tweepy.Cursor(self.api.friends).items():
            if friend.id not in self.cache['friends']:
                self.cache['friends'].append(friend.id)

    def updateDMs(self):
        # do a call for new dms
        new_dm_call = self.api.list_direct_messages()

        # if no 'dm_cache' exists, create as empty dict
        if not hasattr(self, 'dm_cache'):
            self.dm_cache = {}

        # if there is no 'most_recent' message id, set to zero
        if 'most_recent' not in self.cache:
            self.cache['most_recent'] = 0

        # else, save to cache all DMs more recent than 'most_recent'
        for dm in new_dm_call:
            if int(dm.id) > self.cache['most_recent']:
                self.dm_cache[int(dm.id)] = dm
        self.cache['most_recent'] = max(self.dm_cache.keys())

    def followEveryoneBack(self):
        for follower_id in self.cache['followers']:
            if follower_id not in self.cache['friends']:
                self.api.follow(follower_id)

    def addUser(self, user_id, admin_status=False):
        # if users not cached, create empty list
        if 'users' not in self.cache:
            self.cache['users'] = {'user': [], 'admin': []}

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

        # if user is admin, remove admin
        if user_id in self.cache['users'][1]:
            self.cache['users'][1].remove(user_id)

        # also remove admin from users
            if wipe:
                self.cache['users'][0].remove(user_id)

        # remove non-admin user
        elif user_id in self.cache['users'][0]:
            self.cache['users'][0].remove(user_id)

    def addStatus(self, status):
        self.cache['statuses'].append(status)

    def removeStatus(self, status):
        self.cache['statuses'].remove(status)

    def groupConversations(self):
        # if no hash exists, create one
        if 'conversations' not in self.cache:
            self.cache['conversations'] = {}

        # check every cached message to see if it is in a conversation
        for message_id in self.dm_cache.keys():
            user_id = int(
                self.dm_cache[message_id].message_create['sender_id'])

            # begin a conversation
            if user_id not in self.cache['conversations'].keys():
                self.cache['conversations'][user_id] = []

            # continue a conversation
            if message_id not in self.cache['conversations'].values():
                self.cache['conversations'][user_id].append(message_id)

    def zombieTweet(self, interval=60, duration=1):
            # tweet a random status from cache['statuses']
            for i in range(duration):
                tweet = random.choice(self.cache['statuses'])
                print(tweet)
                self.api.update_status(status=tweet)
                if duration > 1:
                    time.sleep(interval*duration)

    def returnHashtags(message):
        tags = []
        for tag in message.\
                message_create['message_data']['entities']['hashtags']:
            tags.append(tag['text'])
        return tags

    def checkPermissions(self, user_id):
        permissions = 0
        commands = []
        # check every message in a conversation
        for message in self.cache['conversations'][user_id]:
            commands.append(self.returnHashtags(message))
        return permissions, commands

    def performCommand(self, command, user_id):
        # User commands
        if user_id in self.cache['users']['user'] or\
                user_id in self.cache['users']['admin']:

            if command == 'remove_self':
                self.removeUser(user_id)
            if command == 'shout_at_admins':
                pass
            if command == 'now':
                pass
            if command == 'rights':
                self.limitHandled(self.api.send_direct_message(
                        user_id, str(self.cache['rights'].keys)))

        # Admin commands
        if user_id in self.cache['users']['admin']:
            if command == 'remove_phrase':
                pass
            if command == 'add_phrase':
                pass
            if command == 'vote_remove_admin':
                pass
            if command == 'remove_user':
                pass
            if command == 'add_user':
                pass
            if command == 'vote_admin':
                pass
            if command == 'wipe_self':
                pass
            if command == 'demote_self':
                pass
