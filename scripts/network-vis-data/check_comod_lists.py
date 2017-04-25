#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 17:51:23 2017

@author: emg
"""
import pandas as pd

mods = pd.read_csv('/Users/emg/Programming/GitHub/subreddit-visuals/tidy_data/mods/td-mod-hist.csv', index_col=0)

a = mods[mods['permissions']=='+all']
a.drop_duplicates('name',inplace=True, keep='last')
a.sort_values('pubdate',inplace=True)

a[['name','pubdate']]
