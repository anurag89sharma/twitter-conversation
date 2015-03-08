from django.conf.urls import patterns, include, url
from views import homepage,user_timeline
#from views import get_conversations,homepage,user_timeline,homepage2

urlpatterns = patterns( 'conversations.views',
    #url( r'^api/get-conversations/$', get_conversations),
    url( r'^api/user-timeline/$', user_timeline),
    url( r'', homepage),
)