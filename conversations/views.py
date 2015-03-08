import sys
import json
import requests
from datetime import datetime,timedelta
from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from twython import Twython
from django.template.response import TemplateResponse
# Create your views here.

def homepage(request):
    template = 'tweets/homepage.html'
    response = TemplateResponse(request, template, locals())
    return response

def user_timeline(request):
    # Get APP_KEY and other relevant variables to call the Twython API to collect tweets
    APP_KEY = settings.APP_KEY
    APP_SECRET = settings.APP_SECRET
    ACCESS_TOKEN = settings.ACCESS_TOKEN
    cache_duration = settings.CACHE_DURATION
    t1 = Twython(APP_KEY, access_token=ACCESS_TOKEN)

    # Code to execute when a user enters Twitter Handles and hit submit
    if request.POST:
        # Get twitter Handles of both the user
        screen_name1 = request.POST.get('screen_name1')
        screen_name2 = request.POST.get('screen_name2')
        # Set these twitter handles in memcache for further use
        cache.set('screen_name1', screen_name1, cache_duration)
        cache.set('screen_name2', screen_name2, cache_duration)
        #cache.set('current_time', datetime.now() + timedelta(days=-1),cache_duration)

        # Set the current time in memcache. This is used to fetch tweets from the current instant onwards
        cache.set('current_time', datetime.now(),cache_duration)

        # Fetch the 2 most recent tweet from both the twitter handles
        tweets1 = t1.get_user_timeline(screen_name=screen_name1,contributor_details='true',count=2)
        tweets2 = t1.get_user_timeline(screen_name=screen_name2,contributor_details='true',count=2)

        # Get the common conversation between the 2 twitter handles
        conversations = get_conversation_tweets(tweets1, tweets2, screen_name1, screen_name2)

        template = 'tweets/base_page.html'
        response = TemplateResponse(request, template, locals())
        return response
    else:
        # Code to be called for subsequent GET request to fetch the conversation in real time

        # Fetch the twitter handles from memcache
        screen_name1 = cache.get('screen_name1')
        screen_name2 = cache.get('screen_name2')
        # Get the last tweet_id from memcache
        last_tweet_id = cache.get('last_tweet_id')

        # Fetch the recent tweets since the last tweet_id from both the twitter handles
        tweets1 = t1.get_user_timeline(screen_name=screen_name1,contributor_details='true',since_id=last_tweet_id)
        tweets2 = t1.get_user_timeline(screen_name=screen_name2,contributor_details='true',since_id=last_tweet_id)
        # Get the common conversation between the 2 twitter handles
        conversations = get_conversation_tweets(tweets1, tweets2, screen_name1, screen_name2)
    
        template = 'tweets/conversation.html'
        return TemplateResponse(request, template, locals())
        #return HttpResponse(json.dumps(conversations))

def get_conversation_tweets(tweets1, tweets2, screen_name1, screen_name2):
    cache_duration = settings.CACHE_DURATION
    # Get the conversation tweets for 1st twitter handle
    conversations = get_conversation_tweets_of_single_user(tweets1,screen_name2)
    # Get the conversation tweets for 2nd twitter handle
    conversations.extend(get_conversation_tweets_of_single_user(tweets2,screen_name1))
    # Sort the conversations with respect to time
    conversations = sorted(conversations, key=lambda k: k['time']) 
    # store last conversation tweet_id in memcache
    if len(conversations) > 0:
        cache.set('last_tweet_id', conversations[-1]['tweet_id'], cache_duration)
    for items in conversations:
        items['time'] = str(items['time'])

    return conversations

def get_conversation_tweets_of_single_user(tweets,screen_name):
    conversations = []
    # Get current time from memcache
    current_time = cache.get('current_time')
    # format string to parse the time returned by the twitter api
    formatter_string = "%a %b %d %H:%M:%S +0000 %Y"
    for items in tweets:
        data = {}
        time_of_tweet = datetime.strptime(items['created_at'], formatter_string)
        users = items['entities']['user_mentions']
        for user in users:
            # Check if the tweet is addressed to the twitter handle "screen_name" and
            # the time of tweet is greater than the time at which this app is started
            if user['screen_name'] == screen_name and current_time <= time_of_tweet:
                data['time'] =  time_of_tweet
                data['tweet_text'] = items['text']
                data['tweet_id'] = items['id']
                data['replier'] = items['user']['screen_name']
                data['replier_fullname'] = items['user']['name']
                conversations.append(data)
                break
    return conversations