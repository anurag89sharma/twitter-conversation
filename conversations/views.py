import sys
import json
import requests
import pprint
#from lxml import html,etree
from datetime import datetime,timedelta
from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from twython import Twython
#from django.views.decorators.csrf import csrf_exempt
from django.template.response import TemplateResponse
# Create your views here.

def homepage(request):
    template = 'tweets/homepage.html'
    response = TemplateResponse(request, template, locals())
    return response
    #return HttpResponse(json.dumps("HI"))

def user_timeline(request):

    APP_KEY = settings.APP_KEY
    APP_SECRET = settings.APP_SECRET
    ACCESS_TOKEN = settings.ACCESS_TOKEN
    cache_duration = settings.CACHE_DURATION
    t1 = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    #tweet_id = 573079589137747968
    if request.POST:
        screen_name1 = request.POST.get('screen_name1')
        screen_name2 = request.POST.get('screen_name2')
        cache.set('screen_name1', screen_name1, cache_duration)
        cache.set('screen_name2', screen_name2, cache_duration)
        #cache.set('current_time', datetime.now() + timedelta(days=-1),cache_duration)
        cache.set('current_time', datetime.now(),cache_duration)
        tweets1 = t1.get_user_timeline(screen_name=screen_name1,contributor_details='true',count=2)
        tweets2 = t1.get_user_timeline(screen_name=screen_name2,contributor_details='true',count=2)
        conversations = get_conversation_tweets(tweets1, tweets2, screen_name1, screen_name2)
        #pprint.pprint(conversations)
        template = 'tweets/base_page.html'
        response = TemplateResponse(request, template, locals())
        return response
    else:
        screen_name1 = cache.get('screen_name1')
        screen_name2 = cache.get('screen_name2')
        last_tweet_id = cache.get('last_tweet_id')
        #last_tweet_id = 574116879423250432
        tweets1 = t1.get_user_timeline(screen_name=screen_name1,contributor_details='true',since_id=last_tweet_id)
        tweets2 = t1.get_user_timeline(screen_name=screen_name2,contributor_details='true',since_id=last_tweet_id)
        conversations = get_conversation_tweets(tweets1, tweets2, screen_name1, screen_name2)
        #pprint.pprint(conversations)
    
        template = 'tweets/conversation.html'
        return TemplateResponse(request, template, locals())
        #return HttpResponse(json.dumps(conversations))

def get_conversation_tweets(tweets1, tweets2, screen_name1, screen_name2):
    cache_duration = settings.CACHE_DURATION
    conversations = get_conversation_tweets_of_single_user(tweets1,screen_name2)
    conversations.extend(get_conversation_tweets_of_single_user(tweets2,screen_name1))
    conversations = sorted(conversations, key=lambda k: k['time']) 
    # store last conversation time in memcache
    if len(conversations) > 0:
        cache.set('last_tweet_id', conversations[-1]['tweet_id'], cache_duration)
    for items in conversations:
        items['time'] = str(items['time'])

    return conversations

def get_conversation_tweets_of_single_user(tweets,screen_name):
    conversations = []
    current_time = cache.get('current_time')
    formatter_string = "%a %b %d %H:%M:%S +0000 %Y"
    for items in tweets:
        data = {}
        time_of_tweet = datetime.strptime(items['created_at'], formatter_string)
        users = items['entities']['user_mentions']
        for user in users:
            if user['screen_name'] == screen_name and current_time <= time_of_tweet:
                data['time'] =  time_of_tweet
                data['tweet_text'] = items['text']
                data['tweet_id'] = items['id']
                data['replier'] = items['user']['screen_name']
                data['replier_fullname'] = items['user']['name']
                conversations.append(data)
                break
    return conversations