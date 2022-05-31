#!/usr/bin/env python
# coding: utf-8

# # Social Metrics

# In[1]:


import json
import glob
import pandas as pd
import altair as alt
import pprint


# In[2]:


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


# In[3]:


tweets = pd.DataFrame(holder)
tweets['created_at'] = pd.to_datetime(tweets['created_at'])
tweets.index = tweets['id']
del(tweets['id'])
print(tweets.info())


# In[4]:


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


# ## Retweets, Quote Tweets, Likes and Replies

# In[5]:


grouper = tweets.groupby('account')
holder = []
for a, b in grouper:
    temp = b[['likes', 'quotes', 'replies', 'retweets']].copy()
    temp['account'] = a
    holder.append(temp)


# In[6]:


metrics = pd.concat(holder)
z=metrics.describe()
z.style.format(precision=0, na_rep='MISSING', thousands=",")


# In[7]:


grouper = tweets.groupby('account')
holder = []
for a, b in grouper:
    temp = pd.DataFrame(b[['likes', 'quotes', 'replies', 'retweets']].unstack())
    temp.reset_index(inplace=True)
    temp['account'] = a
    holder.append(temp)


# In[8]:


chart_metrics = pd.concat(holder)

chart_metrics.rename(columns={0:"value", "level_0":"metric"}, inplace=True)
del(chart_metrics['id'])
chart_metrics.info()


# In[9]:


alt.data_transformers.disable_max_rows()


# In[10]:


metrics_boxplot = alt.Chart(
    chart_metrics).mark_boxplot(
).encode(x=alt.X('account:N', axis=alt.Axis(title="")),
         y=alt.Y('value:Q', axis=alt.Axis(title="count of metric")),
         tooltip=["account",
                  "metric",
                  "value"]).properties(
    width=200,
    title="Public Metrics").facet(
    'metric:N', columns=2)

metrics_boxplot


# In[11]:


tweets[tweets.likes==tweets.likes.max()]


# ## Most Liked Tweet
# 
# RTÉ have the most liked tweet of the bunch with 3,825 likes. What was the tweet about?

# In[12]:


print(tweets.loc["1522223815044050944"]['text'])
print(tweets.loc["1522223815044050944"]['created_at'].strftime("%B %d, %H:%M"))


# The next-most liked tweet is from the Independent:

# In[13]:


tweets[(tweets.account=='independent_ie')&(tweets.likes==2603)]


# In[14]:


print(tweets.loc["1521055649748160512"]['text'])
print(tweets.loc["1521055649748160512"]['created_at'].strftime("%B %d, %H:%M"))


# ## Most Replies
# 
# The tweet with the most replies is also from the Independent:

# In[15]:


tweets[(tweets.account=='independent_ie')&(tweets.replies==1214)]


# In[16]:


print(tweets.loc["1522224352930013185"]['text'])
print(tweets.loc["1522224352930013185"]['created_at'].strftime("%B %d, %H:%M"))


# ## Most Retweets
# 
# The tweet with the most likes is also the tweet with the most retweets - RTÉ's tweet about the President's remarks on Elon Musk's purchase of Twitter.

# In[17]:


tweets[(tweets.account=='rtenews')&(tweets.retweets==786)]


# In[18]:


print(tweets.loc["1522223815044050944"]['text'])
print(tweets.loc["1522223815044050944"]['created_at'].strftime("%B %d, %H:%M"))

