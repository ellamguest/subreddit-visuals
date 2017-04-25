#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 12:00:37 2017

@author: emg
"""

import pandas as pd

# from get_mod_subs
df = pd.read_csv('/Users/emg/Programming/GitHub/the_donald_project/raw_data/all_sub_mods.csv',
                 index_col=0)


def get_mod_type(name, mode):
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

def get_lists(df):
    ''' return edgelist, nodelist from df with
        colums (moderator) 'name' and 'sub'
    '''
    edgelist = df[['name','sub']]
    nodelist = pd.DataFrame(list(set(df['name'])) + list(set(df['sub'])))
    modes = [0]*len(list(set(df['name']))) + [1]*len(list(set(df['sub'])))
    nodelist['type'] = modes
    nodelist['name']=nodelist[0].apply(lambda x: x.strip('r/'))
    nodelist['mod_types'] = nodelist.apply(lambda row: get_mod_type(row['name'], row['type']), axis=1)
    return edgelist, nodelist

# limit to subs and mods w/ d > 1
sub_count = df.groupby('sub')['sub'].count()
repeats = sub_count[sub_count>1].index
subset = df[df['sub'].isin(repeats)]
mod_count = subset.groupby('name')['name'].count()
repeats = mod_count[mod_count>1].index
subset = subset[subset['name'].isin(repeats)]

edgelist, nodelist = get_lists(subset)

#edgelist.to_csv('/Users/emg/Programming/GitHub/cmv/tidy_data/edgelist_subset.csv', index=False)
#nodelist.to_csv('/Users/emg/Programming/GitHub/cmv/tidy_data/nodelist_subset.csv', index=False)

edgelist.to_csv('/Users/emg/Programming/GitHub/the_donald_project/tidy_data/edgelist_subset.csv', index=False)
nodelist.to_csv('/Users/emg/Programming/GitHub/the_donald_project/tidy_data/nodelist_subset.csv', index=False)



'''
add mod type attribute to nodelist
0 = subreddit
1 = never td mod
2 = former td non-top mod
3 = former td top mod
4 = current td non-top mod
5 = current td top mod
'''

mods = pd.read_csv('/Users/emg/Programming/GitHub/cmv/tidy_data/dated_mod_df.csv', index_col=0)
mods.sort_values('pubdate',inplace=True)

#modes = [0]*len(list(set(df['name']))) + [1]*len(list(set(df['sub'])))
#nodelist['type'] = modes
mod_names = nodelist[nodelist['type']==0][0]
current = mods.sort_values('pubdate')['pubdate'].tail(1)

   