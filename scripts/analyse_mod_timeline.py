#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 15:46:10 2017

@author: emg
"""

import pandas as pd
from create_mod_timeline import *
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap

sns.set_style("white") # set aes to white w/out grid

## IMPORT DATA

# CMV data
df = pd.read_csv('/Users/emg/Programming/GitHub/cmv/tidy_data/dated_mod_df.csv', index_col=0)
df['pubdate'] = df['pubdate'].astype(str)
df['pubdate'] = df['pubdate'].apply(lambda t:'{}/{}/{}'.format(t[:4],t[4:6],t[6:8]))
df['perm_level'] = df['permissions'].map(
        {'+access,-config,-flair,-mail,+posts,-wiki':2,
             '+access,-config,+flair,+mail,+posts,-wiki':3,
             '+all':4}
        ).fillna(1)

df['permissions'].value_counts()

# TD data
df = pd.read_csv('/Users/emg/Programming/GitHub/the_donald_project/raw_data/all_mods_merged.csv', index_col=1)
df['perm_level'] = df['permissions'].map(
        {'+access,-config,-flair,-mail,+posts,-wiki':2,
             '+access,-config,+flair,+mail,+posts,-wiki':3,
             '+all':4}
        ).fillna(1)


## CREATE AND PLOT WEEKLY TIMELINE
timeline = timeline_df(df)
weeks = timeline.resample('W').last()
names = list(df.sort_values('date')['name'].drop_duplicates())
weeks = weeks[names]

months = weeks.resample('M').last()
months.index = months.index.map(lambda x: x.date())


def basic_plot():
    mask = weeks.replace(0, np.nan).isnull() # mask 0s
    fig, ax = plt.subplots(figsize=(9,13))
    sns.heatmap(weeks, cmap='Set1', mask=mask)
    plt.title('Timeline of Moderator Presence & Permissions', fontsize=20)
    plt.ylabel('Date (in weeks)', fontsize=15)
    plt.xlabel('Moderator', fontsize=15)
    plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/cmv-timeline.png')   

#BETTER COLOURED PLOT
colours = ('white','orange','green','red','blue')
cmap = LinearSegmentedColormap.from_list('Custom',colours, len(colours))
ax=sns.heatmap(month, cmap=cmap)
colorbar = ax.collections[0].colorbar
colorbar.set_ticks([0, 1, 2, 3, 4])
colorbar.set_ticklabels(['', 'A', 'B', 'C', 'all'])



# testing qualitative color palette
current_palette = sns.color_palette()
colours = sns.color_palette('Dark2', 3)
sns.palplot(current_palette)

my_palette = sns.color_palette(['white','firebrick','indigo'], 3)
sns.palplot(my_palette)
