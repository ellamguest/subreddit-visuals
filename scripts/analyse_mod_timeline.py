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

## IMPORT DATA and MAKE MONTHLY TIMELINE
# CMV data
def cmv_data():
    df = pd.read_csv('/Users/emg/Programming/GitHub/cmv/tidy_data/dated_mod_df.csv', index_col=0)
    df['pubdate'] = df['pubdate'].astype(str)
    df['pubdate'] = df['pubdate'].apply(lambda t:'{}/{}/{}'.format(t[:4],t[4:6],t[6:8]))
    df['perm_level'] = df['permissions'].map(
            {'+access,-config,-flair,-mail,+posts,-wiki':2,
                 '+access,-config,+flair,+mail,+posts,-wiki':3,
                 '+all':4}
            ).fillna(1)
    return df

# TD data
def td_data():
    df = pd.read_csv('/Users/emg/Programming/GitHub/the_donald_project/raw_data/all_mods_archive_it_04_17.csv')
    df['perm_level'] = df['permissions'].map(
            {'+access,-config,-flair,-mail,+posts,-wiki':2,
                 '+access,-config,+flair,+mail,+posts,-wiki':3,
                 '+all':4}
            ).fillna(1)
    return df

# CREATE AND PLOT MONTHLY TIMELINE
def monthly_timeline(df):
    timeline = timeline_df(df)
    months = timeline.resample('M').last()
    months.index = months.index.map(lambda x: x.date())
    return months

##BETTER COLOURED PLOT
colours = ('white','orange','green','red','blue')
cmap = LinearSegmentedColormap.from_list('Custom',colours, len(colours))

def plot(months, sub='?'):
    #sub defaults to ? unless name is given to save plot as
    fig, ax = plt.subplots(figsize=(15,13))
    ax=sns.heatmap(months, cmap=cmap)
    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6])
    colorbar.set_ticklabels(['not present', 'other perm types',
                             '+ access, posts', '+ access, flair, mail, posts',
                             'all'])
    plt.title('Timeline of Moderator Presence & Permissions',
              fontsize=24, fontweight='bold')
    plt.ylabel('Date (in months)', fontsize=15)
    plt.xlabel('Moderator', fontsize=15)
    plt.tick_params(axis='y',which='major', labelsize=12)
    plt.tick_params(axis='x',which='major', labelsize=0)
    plt.tight_layout()
    plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/{}-timeline.png'.format(sub))   

## CREATE TD PLOT
df1 = td_data() 
months1 = monthly_timeline(df1)
plot(months, 'td')

## CREATE CMV PLOT
df2 = cmv_data() 
months2 = monthly_timeline(df2)
plot(months, 'cmv')



## attempting custon legend

#Get artists and labels for legend and chose which ones to display
handles, labels = ax.get_legend_handles_labels()
display = (0,1,2)

#Create custom artists
simArtist = plt.Line2D((0,1),(0,0), color='k', marker='o', linestyle='')
anyArtist = plt.Line2D((0,1),(0,0), color='k')

#Create legend from custom artist/label lists
ax.legend([handle for i,handle in enumerate(handles) if i in display]+[simArtist,anyArtist],
          [label for i,label in enumerate(labels) if i in display]+['Simulation', 'Analytic'])

df1 = td_data() 
months1 = monthly_timeline(df1)
months1.index = months1.index.map(lambda x: '{}-{:02d}'.format(x.year,x.month))

df2 = cmv_data() 
months2 = monthly_timeline(df2)


fig, axn = plt.subplots(1, 2, sharex=True, sharey=True)
#cbar_ax = fig.add_axes([.91, .3, .03, .4])
for i, ax in enumerate(axn.flat):
    sns.heatmap(df, ax=ax,
                cbar=i == 0,
                vmin=0, vmax=1),
                cbar_ax=None if i else cbar_ax)

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(30,13))
g1 = sns.heatmap(months1,cmap=cmap,cbar=False,ax=ax1)
g1.set_ylabel('')
g1.set_xlabel('')
g2 = sns.heatmap(months2,cmap=cmap,ax=ax2)
g2.set_ylabel('')
g2.set_xlabel('')    
colorbar = ax2.collections[0].colorbar
colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6])
colorbar.set_ticklabels(['not present', 'other perm types',
                         '+ access, posts', '+ access, flair, mail, posts',
                         'all'])
colorbar.ax.tick_params(labelsize=20)
ax1.set_title('TD Moderator Timeline', fontsize=24)
ax2.set_title('CMV Moderator Timeline', fontsize=24)
ax1.set_xticklabels(list(months1.index.map(lambda x: '{}-{}'.format(x.year,x.month))))
ax1.set_xlabel('TD Moderators', fontsize=20)
ax1.set_ylabel('Date (in months)', fontsize=20)
ax2.set_xlabel('CMV Moderators', fontsize=20)
ax1.tick_params(axis='y',which='major', labelsize=12)
ax1.tick_params(axis='x',which='major', labelsize=0)
ax2.tick_params(axis='y',which='major', labelsize=10)
ax2.tick_params(axis='x',which='major', labelsize=0)
plt.tight_layout()
plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/joint-timelines.png')