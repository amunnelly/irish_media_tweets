#!/usr/bin/env python
# coding: utf-8

# # Irish Media Twitter Activity

# In[1]:


import json
import glob
import pandas as pd
import altair as alt
import pprint


# The data was to comprise of tweets taken from five twitter accounts for the five biggest media organisations in Ireland:
# * RTÉ News
# * ~~The Irish Times~~
# * The Irish Independent
# * The Irish Examiner
# * The Journal (Dot IE)
# 
# 
# ### Missing Irish Times Data
# 
# This work was done in the last week in May, 2022. At the start of the week, there was no problem accessing the Irish Times tweets. At the end of the week, when testing had finished and I looked at a bigger tweet selection, all I got back from the Irish Times was `[{"meta": {"result_count": 0}}]`. I have no idea why, and had no option but to proceed without them.

# ## The Individual Accounts

# In[2]:


files = glob.glob('tweets/newspapers/newspaper_account_details/*.json')
media_details = []
for f in files:
    with open(f) as g:
        temp = json.load(g)
        media_details.append(temp)


# A look at how the information is organised.

# In[3]:


pprint.pprint(media_details[0]['data'])


# In[4]:


holder = []
for detail in media_details:
    temp = {"created_at": detail['data']['created_at'],
            "username": detail['data']['username'],
            "name": detail['data']['name'],
            "id": detail['data']['id'],
            "followers": detail['data']['public_metrics']['followers_count'],
            "following": detail['data']['public_metrics']['following_count'],
            "listed": detail['data']['public_metrics']['listed_count'],
            "tweets": detail['data']['public_metrics']['tweet_count'],
            "location": detail['data']['location'],
            "verified": detail['data']['verified']}
    holder.append(temp)


# In[5]:


media_df = pd.DataFrame(holder)
media_df.index = media_df['id']
del(media_df['id'])
media_df['created_at'] = pd.to_datetime(media_df['created_at'])
media_df


# Add a followers per tweet metric, and sort by followers descending.

# In[6]:


media_df['followers_per_tweet'] = media_df['followers'] / media_df['tweets']
media_df.sort_values('followers', ascending=False)


# ## Charts for Followers per Account, Followers per Tweet per Account

# In[7]:


bar = alt.Chart(media_df).mark_bar().encode(x='name',
                                            y='followers',
                                           tooltip=['name', 'followers']).properties(title='Followers per Acccount',
                                                                      width=300)
bar2 = alt.Chart(media_df).mark_bar(color='crimson').encode(x='name',
                                                            y='followers_per_tweet',
                                           tooltip=['name', 'followers_per_tweet']).properties(title='Followers per Tweet per Acccount',
                                                                      width=300)
bar | bar2


# Examine correlation, if any, in the numeric data.

# In[8]:


media_df.corr()


# ## Observations
# 
# * RTÉ is the big beast of Irish media twitter, just as it’s the big beast of Irish media in general. It has the the most followers and has the longest-established account.
# * There’s quite a close correlation between follower count and number of tweets - a Pearson co-efficient of 0.88. However, this is more than likely a co-incidence. Closer examination of the growth of the accounts may be more illustrative. It is not reasonable to suggest that a relationship exists between tweets and followers.
# * The Journal follows the most accounts, and the Independent the least.
# * The Independent lists its location as Dublin, while the other four list theirs as Ireland.

# # The Tweets

# In[9]:


with open('tweets/newspapers/recent_tweets/independent_ie.json') as f:
    indo = json.load(f)
type(indo)


# In[10]:


pprint.pprint(indo[0]['data'][0])


# ## Assembling the Tweet Data

# In[11]:


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


# In[12]:


tweets = pd.DataFrame(holder)
tweets['created_at'] = pd.to_datetime(tweets['created_at'])
tweets.index = tweets['id']
del(tweets['id'])
print(tweets.info())


# In[13]:


tweets.head()


# ## Tweets per Account

# In[14]:


tpa = pd.DataFrame(tweets.account.value_counts())
tpa.rename(columns={"account":"tweets"}, inplace=True)
tpa


# ## Sources

# In[15]:


pd.crosstab(tweets.source, tweets.account)


# In[16]:


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


# In[17]:


results = tweet_finder(tweets, 'source', 'Twitter for iPhone', 'irishexaminer')


# In[18]:


for r in results:
    print(r['created_at'])
    print(r['text'])
    print("-"*80)


# ## Reply Settings

# In[19]:


pd.crosstab(tweets.reply_settings, tweets.account)


# ### Replies Limited to Mentioned Users

# `thejournal_ie` limits the reply settings for four of its tweets to "mentionedUsers". Why would this be? to discover, we create  a dataframe, `mu`, by slicing `tweets`.

# In[20]:


results = tweet_finder(tweets, 'reply_settings', 'mentionedUsers', 'thejournal_ie')


# In[21]:


for r in results:
    print(r['created_at'])
    print(r['text'])
    print("-"*80)


# These are sensitive stories, but they are not flagged as such in `entities`. It may be an in-the-moment authorial decision - all four tweets are from the `Twitter Web App` source, which suggests they are not automated.

# ## Retweets, Quote Tweets, Likes and Replies

# In[22]:


grouper = tweets.groupby('account')
holder = []
for a, b in grouper:
    temp = b[['likes', 'quotes', 'replies', 'retweets']].copy()
    temp['account'] = a
    holder.append(temp)


# In[23]:


metrics = pd.concat(holder)
metrics.describe()


# In[24]:


grouper = tweets.groupby('account')
holder = []
for a, b in grouper:
    temp = pd.DataFrame(b[['likes', 'quotes', 'replies', 'retweets']].unstack())
    temp.reset_index(inplace=True)
    temp['account'] = a
    holder.append(temp)


# In[25]:


chart_metrics = pd.concat(holder)

chart_metrics.rename(columns={0:"value", "level_0":"metric"}, inplace=True)
del(chart_metrics['id'])
chart_metrics.info()


# In[26]:


alt.data_transformers.disable_max_rows()


# In[27]:


metrics_boxplot = alt.Chart(chart_metrics).mark_boxplot().encode(x='account:N',
                                                                 y='value:Q',
                                                                 column='metric:N',
                                                                tooltip=["account",
                                                                         "metric",
                                                                         "value"]).properties(width=200,
                                                                                             title="Public Metrics")
metrics_boxplot


# In[28]:


tweets[tweets.likes==tweets.likes.max()]


# In[29]:


print(tweets.loc["1522223815044050944"]['text'])


# In[30]:


tweets[(tweets.account=='independent_ie')&(tweets.likes==2603)]


# In[31]:


print(tweets.loc["1521055649748160512"]['text'])


# ### Most Replies

# In[32]:


tweets[(tweets.account=='independent_ie')&(tweets.replies==1214)]


# In[33]:


print(tweets.loc["1522224352930013185"]['text'])


# In[34]:


tweets[(tweets.account=='rtenews')&(tweets.replies==824)]


# In[35]:


print(tweets.loc["1522223815044050944"]['text'])


# ## Tweet Dates and Times

# ### Starts and Finishes

# ### Hourly

# In[36]:


date_range = pd.date_range(start="2022-05-01 00:00:00+00:00", end=tweets.created_at.max(), freq='H')
len(date_range)


# In[37]:


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


# In[38]:


time_df = pd.concat(holder)
time_df.info()


# In[39]:


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


# In[40]:


alt.Chart(chart_df).mark_line().encode(x='created_at:T',
                                       y='value:Q',
                                       color='account',
                                       column='metric',
                                      tooltip=["created_at",
                                               "value",
                                               "account"]).interactive()


# ## Tweet Times

# In[41]:


tweets.head()


# In[42]:


temp = tweets.copy()
temp['hour'] = temp.created_at.apply(lambda x: x.strftime('%H:00'))
holder = []
grouper = temp.groupby(['account', 'hour'])
for a, b in grouper:
    holder.append([a[0], a[1], b.shape[0]])


# In[43]:


tweet_times = pd.DataFrame(holder, columns=["account", "time", "tweets"])
tweet_times.info()


# In[44]:


len(tweet_times.time.unique())


# In[45]:


heatmap = alt.Chart(tweet_times).mark_rect().encode(x='time:O',
                                                    y='account:N',
                                                    color='tweets:Q',
                                                   tooltip=['time',
                                                            'account',
                                                            'tweets']).properties(width=600,
                                                                                  height=200,
                                                                                  title='Tweets per Hour')

heatmap


# ## Tweets by Account by Source

# In[46]:


temp = tweets.copy()
temp['hour'] = temp.created_at.apply(lambda x: x.strftime('%H:00'))
holder = []
grouper = temp.groupby(['account','source', 'hour'])
for a, b in grouper:
    holder.append([a[0], a[1], a[2], b.shape[0]])


# In[47]:


tweet_times = pd.DataFrame(holder, columns=["account", "source", "time", "tweets"])
tweet_times.info()


# In[48]:


source_df = pd.pivot_table(tweet_times, index=['account', 'source'], columns=['time'], values=['tweets'])
source_df.reset_index(inplace=True)
source_df.head()


# In[49]:


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


# In[50]:


b.head()


# In[51]:


base = alt.Chart(tweet_times).mark_rect().encode(
    x=alt.X('time:O', axis=alt.Axis(title="")),
    y=alt.Y('source:O', axis=alt.Axis(title="")),
    color='tweets:Q',
    tooltip=["time", "source", "account", "tweets"]
).properties(
    width=350,
    height=200,
    title='zebadee'
).facet('account:N', columns=2)

base

