#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 14:23:59 2017

@author: emg
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json


### GETTING REDDIT API CREDENTIALS
with open('credentials.json', 'r') as f:
     data = json.load(f)

headers={'User-agent':data['user_agent']}

### UPDATE CMV + TD MOD TIMELINES
import update_cmv_mod_hist
import update_td_mod_hist

### LOAD TIMELINE MOD HIST DATA
td_df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/td-mod-hist.csv', index_col=0)
cmv_df = pd.read_csv('/Users/emg/Programming/GitHub/mod-timelines/tidy-data/cmv-mod-hist.csv', index_col=0)

df = pd.read_csv('/Users/emg/Programming/GitHub/subreddit-visuals/tidy_data/mods/td-mod-hist.csv', index_col=0)

names = list(set((df[df['name']!='AutoModerator']['name'])))


def make_soup(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    return soup

d = {}
errors = []
for name in names:
    print name
    url = 'https://www.reddit.com/user/{}'.format(name)
    soup = make_soup(url)
    try:
        table = soup.find('ul', {'id':'side-mod-list'})
        items = table.find_all('li')
        subs = []
        for item in items:
            subs.append(item.a['title'])
        d[name] = subs
    except:
        errors.append(name)
        pass

errors2 = []
for name in errors[0]:
    print name
    url = 'https://www.reddit.com/user/{}'.format(name)
    soup = make_soup(url)
    try:
        table = soup.find('ul', {'id':'side-mod-list'})
        items = table.find_all('li')
        subs = []
        for item in items:
            subs.append(item.a['title'])
        d[name] = subs
    except:
        errors2.append(name)
        pass

d = {}
errors3 = []
for sub in subs:
    print sub
    try:
        url = 'https://www.reddit.com/{}/about/moderators'.format(sub)
        print url
        soup = make_soup(url)
        table = soup.find('div',{'class':'moderator-table'})
        items = table.find_all(href=re.compile("/user/"))
        names = []
        for item in items:
            names.append(item.text)
        d[sub] = names
    except:
        errors3.append(sub)
        pass
        

edgelist = [] 
for key in d.keys():
    for value in d[key]:
        edgelist.append([value, key])

edgelist = pd.DataFrame(edgelist)
edgelist.columns = ['name', 'sub']
#td_mods = list(set(df['name']))
#edgelist = edgelist[edgelist['name'].isin(td_mods)]
edgelist.to_csv('/Users/emg/Programming/GitHub/the_donald_project/tidy_data/edgelist_subset.csv', index=False)



def get_mod_type(name, mode=0):
    mods = pd.read_csv('/Users/emg/Programming/GitHub/subreddit-visuals/tidy_data/mods/td-mod-hist.csv', index_col=0)
    current = mods['pubdate'].max()
    subset = mods[mods['name']==name]
    if mode == 1:
        return 1
    if name not in list(mods['name']):
        return 2
    if current not in list(subset['pubdate']):
        if '+all' not in list(subset['permissions']):
            return 3
        else:
            return 4
    if current in list(subset['pubdate']):
        if '+all' not in list(subset['permissions']):
            return 5
        else:
            return 6

def get_nodelist(df):
    ''' return edgelist, nodelist from df with
        colums (moderator) 'name' and 'sub'
    '''
    nodelist = pd.DataFrame(list(set(df['name'])) + list(set(df['sub'])))
    modes = [0]*len(list(set(df['name']))) + [1]*len(list(set(df['sub'])))
    nodelist['type'] = modes
    nodelist['name']=nodelist[0].apply(lambda x: x.strip('r/'))
    nodelist['mod_types'] = nodelist.apply(lambda row: get_mod_type(row['name'], row['type']), axis=1)
    return nodelist

nodelist = get_nodelist(edgelist)


nodelist.to_csv('/Users/emg/Programming/GitHub/the_donald_project/tidy_data/nodelist_subset.csv', index=False)

