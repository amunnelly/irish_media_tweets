#!/usr/bin/env python
# coding: utf-8

# # The Four Individual Accounts

# In[1]:


import json
import glob
import pandas as pd
import altair as alt
import pprint


# In[2]:


files = glob.glob('tweets/newspapers/newspaper_account_details/*.json')
media_details = []
for f in files:
    with open(f) as g:
        temp = json.load(g)
        media_details.append(temp)


# ## Account Metadata

# This is the metadata for a typical twitter account - [@independent_ie](https://twitter.com/Independent_ie) in this case.

# In[3]:


pprint.pprint(media_details[4]['data'])


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

media_df['followers_per_tweet'] = media_df['followers'] / media_df['tweets']
# media_df = media_df.round({'followers_per_tweet':2})
media_df.sort_values('followers', ascending=False, inplace=True)
media_df


# ## The Four Accounts
# 
# This is a table of the four counts, showing when they were created, username and name, and other significant details.

# In[6]:


media_df.style.format(precision=2, thousands=",",
                formatter={'created_at': lambda x: x.strftime('%B %d, %Y')
                          })


# ## Observations
# 
# * RTÉ were the earliest adopters of Twitter, opening their account eighteen months after Twitter was founded.
# * RTÉ are also the most popular account to follow, with 1.1 million followers.
# * RTÉ are not the biggest tweeters however - that honour belongs to the Irish Times, with nearly seven hundred thousand tweets to show for their fourteen year activity.
# * Four of the five accounts set their location as Ireland. Only the Independent specifies Dublin.

# ## Charts Followers per Account, Followers per Tweet per Account

# In[7]:


media_df['followers '] = media_df.followers.apply(lambda x: "{:,}".format(x))
media_df['followers_per_tweet '] = media_df.followers_per_tweet.apply(lambda x: "{:.2f}".format(x))


# In[8]:


bar = alt.Chart(media_df).mark_bar().encode(x=alt.X('name', sort='-y'),
                                            y='followers',
                                           tooltip=['name',
                                                    'followers ']).properties(
                                                                    title='Followers per Acccount',
                                                                      width=300)
bar2 = alt.Chart(media_df).mark_bar(color='crimson').encode(x=alt.X('name', sort='-y'),
                                                            y='followers_per_tweet',
                                           tooltip=['name', 'followers_per_tweet ']).properties(
                                                                        title='Followers per Tweet per Acccount',
                                                                      width=300)
bar | bar2

