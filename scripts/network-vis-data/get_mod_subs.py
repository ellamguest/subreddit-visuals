#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 14:23:59 2017

@author: emg
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
from prawini import *

params = get_params()
headers={'User-agent':params['user_agent']}

df = pd.read_csv('/Users/emg/Programming/GitHub/the_donald_project/raw_data/current-mod-table.csv',
                 index_col=0)

names = list((df[df['name']!='AutoModerator']['name']))


def make_soup(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    return soup

d = {}
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
        pass
    

values = list(set([x for y in d.values() for x in y]))
data = {}
for key in d.keys():
    data[key] = [True if value in d[key] else False for value in values ]

mod_subs = pd.DataFrame(data, index=values)
mod_subs = mod_subs.applymap(lambda x: 1 if x else 0)


subs = list(mod_subs.index)

dfs = []
errors = []
n = 1
for sub in subs:
    try:
        df = scrape_mod_table(sub)
    except:
        errors.append(sub)
        pass
    dfs.append(df)
    n += 1

all_sub_mods = pd.concat(dfs)

all_sub_mods.to_csv('/Users/emg/Programming/GitHub/the_donald_project/raw_data/all_sub_mods.csv')



# then use td_convert to edgelist


