#!/usr/bin/env python
# coding: utf-8

# # The Tweets

# In[1]:


import json
import glob
import pandas as pd
import altair as alt
import pprint


# In[2]:


with open('tweets/newspapers/recent_tweets/independent_ie.json') as f:
    indo = json.load(f)
type(indo)


# In[3]:


pprint.pprint(indo[0]['data'][0])


# ## Assembling the Tweet Data

# In[4]:


files = glob.glob("tweets/newspapers/recent_tweets/*.json")
holder = []
for f in files:
    with open(f) as g:
        tweets = json.load(g)
        for item in tweets:
            for t in item['data']:
                temp = {"id": t["id"],
                    "account": f.split("/")[-1][:-5],
                        "created_at": t["created_at"],
                           "likes": t['public_metrics']["like_count"],
                            "quotes": t['public_metrics']["quote_count"],
                            "replies": t['public_metrics']["reply_count"],
                            "retweets": t['public_metrics']["retweet_count"],
                            "reply_settings": t['reply_settings'],
                            "source": t['source'],
                            "text": t['text']}
                holder.append(temp)


# In[5]:


tweets = pd.DataFrame(holder)
tweets['created_at'] = pd.to_datetime(tweets['created_at'])
tweets.index = tweets['id']
del(tweets['id'])
print(tweets.info())


# These are the metrics of the first five tweets of 1,995.

# In[6]:


tweets.head()


# ## Tweets per Account
# 
# These are the total tweet counts per account.

# In[7]:


tpa = pd.DataFrame(tweets.account.value_counts())
tpa.rename(columns={"account":"tweets"}, inplace=True)
tpa


# ## Tweets by Day By Account
# 
# And these are the tweets by account by day.

# In[8]:


dates = pd.date_range(start='2022-05-01', end='2022-05-07', freq='D')
date_order = []
[date_order.append(x.strftime('%a, %b %d')) for x in dates];


# In[9]:


tbdba = tweets.copy()
tbdba['date'] = tbdba.created_at.apply(lambda x: x.strftime('%a, %b %d'))
temp = pd.crosstab(tbdba.date, tbdba.account)
temp.index = pd.Categorical(temp.index, date_order, ordered=True)
temp.sort_index(inplace=True)
temp


# ## Sources
# 
# The majority of tweets from these news organisations are automated. A number of different platforms are used.
# 
# [Buffer](https://developer.twitter.com/en/community/toolbox/buffer), a social media marketing software used for building brands on social media, is used only by the Irish Independent. [dlvr.it](https://dlvrit.com/) does the same thing, and is used only by the Examiner. [Tweetdeck](https://tweetdeck.twitter.com/) is the favourite of the The Journal, while RTÉ use the Twitter Web App, which is Tweetdeck by another name.

# In[10]:


pd.crosstab(tweets.source, tweets.account)


# In[11]:


def tweet_finder(data, key, value, account):
    sieve = data[data[key]==value]
    holder = []
    with open(f'tweets/newspapers/recent_tweets/{account}.json') as f:
        temp = json.load(f)
    for item in temp:
        for t in item['data']:
            if t['id'] in sieve.index:
                holder.append(t)
    print(f'The result set has {len(holder)} tweets.')
    return holder


# ### Tweets from Twitter for iPhone
# 
# The Examiner over-rode the automation three times during the week to send tweets from an iPhone. Let's look at the tweets.

# In[12]:


results = tweet_finder(tweets, 'source', 'Twitter for iPhone', 'irishexaminer')


# In[13]:


for r in results:
    print(r['created_at'])
    print(r['text'])
    print("-"*80)


# All three are sports columns. It may be that the iPhone tweeter wrote one, if not all, of those columns. It's a reasonable hypothesis.

# ## Reply Settings
# 
# Because bullying is prevalent on Twitter users can set their accounts to either accept responses from everyone, which is the default, or limit it to only those users who are mentioned in the tweet itself. These are the settings for the tweets in the data set.

# In[14]:


pd.crosstab(tweets.reply_settings, tweets.account)


# ### Replies Limited to Mentioned Users

# `thejournal_ie` limits the reply settings for four of its tweets to "mentionedUsers". Why would this be? Again, we can look at the tweets.

# In[15]:


results = tweet_finder(tweets, 'reply_settings', 'mentionedUsers', 'thejournal_ie')


# In[16]:


for r in results:
    print(r['created_at'])
    print(r['text'])
    print("-"*80)

