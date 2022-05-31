#!/usr/bin/env python
# coding: utf-8

# # Tweet Times

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


# ## Tweet Dates and Times

# In[5]:


date_range = pd.date_range(start="2022-05-01 00:00:00+00:00", end=tweets.created_at.max(), freq='H')
len(date_range)


# In[6]:


holder = []
grouper = tweets.groupby('account')
for a, b in grouper:
    temp = b[['created_at', 'likes', 'quotes', 'replies', 'retweets']].copy()
    temp.index=temp['created_at']
    del(temp['created_at'])
    temp = temp.resample('H').sum()
    temp = temp.reindex(date_range)
    temp.fillna(0, inplace=True)
    temp['account'] = a
    temp[['likes', 'quotes', 'replies', 'retweets']] = temp[['likes', 'quotes', 'replies', 'retweets']].cumsum() 
    holder.append(temp)


# In[7]:


time_df = pd.concat(holder)
time_df.info()


# In[8]:


grouper = time_df.groupby('account')
holder = []
for a, b in grouper:
    temp = pd.DataFrame(b.unstack())
    temp.reset_index(inplace=True)
    temp.columns = ["metric", "created_at", "value"]
    temp = temp[temp['metric'] != "account"]
    temp['account'] = a
    holder.append(temp)
    
chart_df = pd.concat(holder)
chart_df['value'] = chart_df['value'].astype(int)
chart_df.info()


# In[9]:


alt.Chart(chart_df).mark_line().encode(x='created_at:T',
                                       y='value:Q',
                                       color='account',
                                      tooltip=["created_at",
                                               "value",
                                               "account"]).properties(
                                                            width=300,
                                                            height=300
                                                            ).facet(
                                                                    "metric:N", columns=2
                                                                    ).interactive()


# In[10]:


tweets.head()


# In[11]:


temp = tweets.copy()
temp['hour'] = temp.created_at.apply(lambda x: x.strftime('%H:00'))
holder = []
grouper = temp.groupby(['account', 'hour'])
for a, b in grouper:
    holder.append([a[0], a[1], b.shape[0]])


# In[12]:


tweet_times = pd.DataFrame(holder, columns=["account", "time", "tweets"])
tweet_times.info()


# In[13]:


len(tweet_times.time.unique())


# ## Tweets by Account by Hour
# 
# This is a heatmap of the total tweets per hour per account. The hours are along the x-axis, the accounts along the y.
# 
# Not every account has the same way of doing it. The Examiner goes heavy between six and seven am, two and three pm, and seven and eight pm. Neither The Journal nor RTÉ want anything to do with the witching hour between midnight and four in the morning. The Independent chugs out tweets every hour, non-stop.

# In[14]:


heatmap = alt.Chart(tweet_times).mark_rect().encode(x='time:O',
                                                    y='account:N',
                                                    color='tweets:Q',
                                                   tooltip=['time',
                                                            'account',
                                                            'tweets']).properties(width=600,
                                                                                  height=200,
                                                                                  title='Tweets per Hour')

heatmap


# ## Tweets by Hour by Account by Source
# 
# And finally, for completeness, here are those tweets broken down further by account and by source.

# In[15]:


temp = tweets.copy()
temp['hour'] = temp.created_at.apply(lambda x: x.strftime('%H:00'))
holder = []
grouper = temp.groupby(['account','source', 'hour'])
for a, b in grouper:
    holder.append([a[0], a[1], a[2], b.shape[0]])


# In[16]:


tweet_times = pd.DataFrame(holder, columns=["account", "source", "time", "tweets"])
tweet_times.info()


# In[17]:


source_df = pd.pivot_table(tweet_times, index=['account', 'source'], columns=['time'], values=['tweets'])
source_df.reset_index(inplace=True)
source_df.head()


# In[18]:


grouper = tweet_times.groupby('account')
holder = []
for a, b in grouper:
    heatmap = alt.Chart(b).mark_rect().encode(x='time:O',
                                                    y='source:N',
                                                    color='tweets:Q',
                                                   tooltip=['time',
                                                            'source',
                                                            'tweets']).properties(title=a)
    holder.append(heatmap)    


# In[19]:


b.head()


# In[20]:


base = alt.Chart(tweet_times).mark_rect().encode(
    x=alt.X('time:O', axis=alt.Axis(title="")),
    y=alt.Y('source:O', axis=alt.Axis(title="")),
    color='tweets:Q',
    tooltip=["time", "source", "account", "tweets"]
).properties(
    width=350,
    height=200,
).facet('account:N', columns=2)

base

