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
    "I am a twitter bot."

    def __init__(self):
        # Authentication
        self.auth = tweepy.OAuthHandler(
                keys.consumer_key, keys.consumer_secret)
        self.auth.set_access_token(
                keys.access_token, keys.access_token_secret)

        self.api = tweepy.API(self.auth)

        # Load most_recent, followers, friends, statuses, rights
        if os.path.exists('cache.pkl'):
            f = open('cache.pkl', 'rb')
            self.cache = dill.load(f)
            f.close()
        else:
            self.cache = {}

        # Load dm_cache
        if os.path.exists('dm_cache.pkl'):
            g = open('dm_cache.pkl', 'rb')
            self.dm_cache = dill.load(g)
            g.close()
        else:
            self.dm_cache = []

        # Load users, votes
        if os.path.exists('users.pkl'):
            g = open('users.pkl', 'rb')
            self.users = dill.load(g)
            g.close()
        else:
            self.users = {}

    def limitHandled(cursor):
        # Check if we have reached the rate limit
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                time.sleep(15*60)

    def writeCache(self):
        # Write out the data stored in the instance
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
        # Update the cached list of followers
        for follower in tweepy.Cursor(self.api.followers).items():
            if follower.id not in self.cache['followers']:
                self.cache['followers'].append(follower.id)

    def updateFriends(self):
        # Update the cached list of friends
        for friend in tweepy.Cursor(self.api.friends).items():
            if friend.id not in self.cache['friends']:
                self.cache['friends'].append(friend.id)

    def updateDMs(self):
        # Update the stored cache of DMs
        new_dm_call = self.api.list_direct_messages()

        # If no 'dm_cache' exists, create as empty dict
        if not hasattr(self, 'dm_cache'):
            self.dm_cache = []

        # If no 'most_recent' message_id exists, set to zero
        if 'most_recent' not in self.cache:
            self.cache['most_recent'] = 0

        # Save to cache all DMs more recent than 'most_recent'
        for dm in new_dm_call:
            if int(dm.id) > self.cache['most_recent']:
                self.dm_cache.append(dm)
        self.cache['most_recent'] = int(self.dm_cache[0].id)

    def followEveryoneBack(self):
        # Follow every single follower
        for follower_id in self.cache['followers']:
            if follower_id not in self.cache['friends']:
                self.api.follow(follower_id)

    def addUser(self, user_id, admin_status=False):
        # If users not cached, create empty list
        if 'users' not in self.cache:
            self.cache['users'] = {'user': [], 'admin': []}

        # Add user to stored list
        self.cache['users']['user'].append(user_id)

        # Grant Admin rights to user
        if admin_status:
            self.cache['users']['admin'].append()

        # Remove duplicate users from stored lists
        self.cache['users']['user'] = set(self.cache['users']['user'])
        self.cache['users']['admin'] = set(self.cache['users']['admin'])

    def removeUser(self, user_id, wipe=False):
        # If users not cached, create empty list
        if 'users' not in self.cache:
            self.cache['users'] = [[], []]

        # If user is Admin, remove Admin rights
        if user_id in self.cache['users'][1]:
            self.cache['users'][1].remove(user_id)

        # Remove admin from list of Users
            if wipe:
                self.cache['users'][0].remove(user_id)

        # Remove normal User from list
        elif user_id in self.cache['users'][0]:
            self.cache['users'][0].remove(user_id)

    def addStatus(self, status):
        # Add a canned tweet to the list
        self.cache['statuses'].append(status)

    def removeStatus(self, status):
        # Remove a canned tweet from the list
        self.cache['statuses'].remove(status)

    def groupConversations(self):
        # If no cached conversations exists, create empty dict
        if 'conversations' not in self.cache:
            self.cache['conversations'] = {}

        # Check every cached message to see if it is in a conversation
        for message_id in self.dm_cache.keys():
            user_id = int(
                self.dm_cache[message_id].message_create['sender_id'])

            # Create a dict for a user_id with a list of messages
            if user_id not in self.cache['conversations'].keys():
                self.cache['conversations'][user_id] = []

            # Add a message to the dictionary of the User
            if message_id not in self.cache['conversations'].values():
                self.cache['conversations'][user_id].append(message_id)

    def zombieTweet(self, interval=60, duration=1):
            # Tweet a random status from cache['statuses']
            for i in range(duration):
                tweet = random.choice(self.cache['statuses'])
                print(tweet)
                self.api.update_status(status=tweet)
                if duration > 1:
                    time.sleep(interval*duration)

    def returnMessageData(message):
        # Parse the message into command, argument, user_id
        command = []
        user_id = message.message_create['sender_id']
        argument = ''
        for tag in message.\
                message_create['message_data']['entities']['hashtags']:
            command.append(tag['text'])
        return command, argument, user_id

    def voteAdmin(self, user_id, target_id):
        # Log a vote to grant Admin rights to a User
        pass

    def voteRemoveAdmin(self, user_id, target_id):
        # Log a vote to demote an Admin
        pass

    def logSighting(self, user_id, location, timestamp):
        # Log who saw police, where, and when
        pass

    def performCommand(self, command, user_id, argument=None):
        # User commands
        if user_id in self.cache['users']['user'] or\
                user_id in self.cache['users']['admin']:

            if command == 'remove_self':
                self.removeUser(user_id, wipe=False)

            if command == 'shout_at_admins':
                for admin in self.users['admin']:
                    self.api.send_direct_message(admin, argument)

            if command == 'now':
                timestamp = 0
                self.logSighting(user_id, argument, timestamp)

            if command == 'rights':
                self.limitHandled(self.api.send_direct_message(
                        user_id, str(self.cache['rights'].keys)))

        # Admin commands
        if user_id in self.cache['users']['admin']:
            if command == 'remove_phrase':
                self.removeStatus(argument)

            if command == 'add_phrase':
                self.addStatus(argument)

            if command == 'vote_remove_admin':
                self.voteRemoveAdmin(user_id, argument)

            if command == 'remove_user':
                self.removeUser(argument, wipe=False)

            if command == 'add_user':
                self.addUser(argument, admin=False)

            if command == 'vote_admin':
                self.voteAdmin(user_id, argument)

            if command == 'wipe_self':
                self.removeUser(user_id, wipe=True)

            if command == 'demote_self':
                self.removeUser(user_id, wipe=False)
