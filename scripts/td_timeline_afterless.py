#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:27:22 2017

@author: emg
"""

import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

### FUCNTIONS TO CONVERT MOD INSTANCES DF TO MOD PRESENCE TIMELINE

def make_after_dict(df):
    '''make d of pubdate: next pubdate to
    apply to df['pubdate'] ot get df['after'] '''
    pubdates = sorted(list(set(df['pubdate'])))
    pubdates.append(datetime.now())
    return dict(zip(pubdates, pubdates[1:]))  

def prep_df(df):
    '''subset df into required columns and types
    to construct timeline df'''
    df['date'] = pd.to_datetime(df['date']).dt.normalize()
    df['pubdate'] = pd.to_datetime(df['pubdate']).dt.normalize()
    after_dict = make_after_dict(df)
    df['after'] = pd.to_datetime(df['pubdate'].map(lambda x:
                                    after_dict[x])).dt.normalize()
    df['perm_level'] = df['permissions'].map(
            {'+access,-config,-flair,-mail,+posts,-wiki':2,
                 '+access,-config,+flair,+mail,+posts,-wiki':3,
                 '+all':4}
            ).fillna(1)
    df.sort_values(['date','pubdate'], inplace=True)
    df.drop_duplicates(['name','date'], keep='last', inplace=True)
    df.set_index('name', inplace=True, drop=False)
    df = df[['name','date','pubdate','after','perm_level']]
    return df

def td_data():
    '''open td moderator instance df'''
    df = pd.read_csv('/Users/emg/Programming/GitHub/subreddit-visuals/tidy_data/mods/td-mod-hist.csv', index_col=0)
    return prep_df(df)

def cmv_data():
    df = pd.read_csv('/Users/emg/Programming/GitHub/cmv/tidy_data/dated_mod_df.csv', index_col=0)
    df['date'] = pd.to_datetime(df['date'])
    df['pubdate'] = pd.to_datetime(df['pubdate'].astype(str), format='%Y%m%d%H%M%S')
    return prep_df(df)

def date_presence_dict(dates, start, end, perm_level): 
    '''check mod presence on date'''
    d = {}
    for date in dates:
        if date >= start and date <= end:
            d[date] = perm_level
    return d

def timeline_df(df):
    '''convert moderator instance date to timeline df'''
    timeline = pd.DataFrame(index = pd.date_range(start = df['date'].min(),
                                                  end = df['pubdate'].max(),
                                                  freq='D'))
    for name in set(df['name']):
        if list(df['name']).count(name) == 1:
            subset = df.loc[name]
            dates = pd.date_range(start = subset['date'],
                                  end = subset['pubdate'],
                                  freq='D')
            start, end, perm_level = subset['date'], subset['pubdate'], subset['perm_level']
            d = date_presence_dict(dates, start, end, perm_level)
            timeline[name] = pd.Series(d)

        elif list(df['name']).count(name) > 1:
            combined = {}
            subset = df.loc[name]
            dates = pd.date_range(start = subset['date'].min(),
                                  end = subset['pubdate'].max(),
                                   freq='D')
            for row in subset.itertuples():
                start, end, perm_level = row[2], row[3], row[5]
                d = date_presence_dict(dates, start, end, perm_level)
                combined.update(d)
            timeline[name] = pd.Series(combined)
    timeline.fillna(0, inplace=True)
    timeline = timeline[list(df.sort_values(['date','pubdate'])['name'].drop_duplicates())]
    return timeline


def monthly_timeline(df):
    timeline = timeline_df(df)
    months = timeline.resample('M').last()
    months.index = months.index.map(lambda x: '{}-{:02d}'.format(x.year,x.month))
    names = months.sum()[months.sum()>0].index
    months = months[names]
    return months

def weekly_timeline(df, min=1):
    #optional arg min to remove modes present for fewer than min weeks
    timeline = timeline_df(df)
    weeks = timeline.resample('W').last()
    weeks.index = weeks.index.map(lambda x: '{}-{:02d}-{:02d}'.format(
                                            x.year,x.month, x.day))
    names = weeks.sum()[weeks.sum()>=min].index
    weeks = weeks[names]   
    return weeks


####### PLOTTING FUNCTIONS
def set_cmap():
    colours = ('white','chocolate','slateblue','seagreen','black')
    cmap = LinearSegmentedColormap.from_list('Custom', colours, len(colours))
    return cmap

def td_plot_H():
    df = td_data()
    td_timeline = timeline_df(df)
    td_timeline = td_timeline[td_timeline.sum()[td_timeline.sum()>60].index]
    
    plt.figure(figsize=(15,15))
    
    ax = sns.heatmap(td_timeline, cmap=set_cmap(), cbar=False)
   
    start, end = ax.get_ylim()
    ax.set_yticks(np.arange(start, end, 60))
    ax.set_yticklabels(list(td_timeline.index.strftime('%Y-%m')[::-60]), fontsize=25)
    plt.tick_params(axis='x',which='both', labelbottom='off')
    
    plt.title('r/The_Donald Moderator Presence Timeline', fontsize=50, y=1.04, fontweight='bold')
    plt.xlabel('r/The_Donald Moderators', fontsize=40,  y=-1.08)
    plt.ylabel('Moderator Presence by Date', fontsize=40, x=-.58)
    
#    colorbar = ax.collections[0].colorbar
#    colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6])
#    colorbar.set_ticklabels(['', 'other perm types',
#                             '+ access, posts', '+ access, flair, mail, posts',
#                             'all'])
    
    plt.tight_layout()
    plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/td-timeline-H.png')

def cmv_plot_H():
    df = cmv_data()
    cmv_timeline = timeline_df(df)
    
    plt.figure(figsize=(30,15))
    
    ax = sns.heatmap(cmv_timeline, cmap=set_cmap())
    start, end = ax.get_ylim()
    ax.set_yticks(np.arange(start, end, 60))
    ax.set_yticklabels(list(cmv_timeline.index.strftime('%Y-%m')[::-60]), fontsize=30)
    plt.tick_params(axis='x',which='both', labelbottom='off')
    
    plt.title('CMV Moderator Presence Timeline', fontsize=60)
    plt.xlabel('r/ChangeMyView Moderators', fontsize=40)
    plt.ylabel('Moderator Presence by Date', fontsize=40)
    
    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6])
    colorbar.set_ticklabels(['', 'Other permission types',
                             'Access and post permissions only', 'Access, flair, mail and posts permissions',
                             'All permissions (Top moderator)'])
    colorbar.ax.tick_params(labelsize=40)
    
    plt.tight_layout()
    plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/cmv-timeline-H.png')

def td_plot_V():
    df = td_data()
    td_timeline = timeline_df(df)
    td_timeline = td_timeline[td_timeline.sum()[td_timeline.sum()>60].index]
    
    plt.figure(figsize=(20,15))
    
    ax = sns.heatmap(td_timeline.T, cmap=set_cmap())
   
    start, end = ax.get_xlim()
    ax.set_xticks(np.arange(start, end, 60))
    ax.set_xticklabels(list(td_timeline.index.strftime('%Y-%m')[::-60]), fontsize=25)
    plt.tick_params(axis='y',which='both', labelleft='off')
    
    plt.title('r/The_Donald Moderator Presence Timeline')
    plt.ylabel('r/The_Donald Moderators', fontsize=40)
    plt.xlabel('Date', fontsize=40)
    
    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6])
    colorbar.set_ticklabels(['', 'other perm types',
                             '+ access, posts', '+ access, flair, mail, posts',
                             'all'])
    
    plt.tight_layout()
    plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/td-timeline-V.png')

def cmv_plot_H():
    df = cmv_data()
    cmv_timeline = timeline_df(df)
    
    plt.figure(figsize=(15,15))
    
    ax = sns.heatmap(cmv_timeline, cmap=set_cmap())
    start, end = ax.get_ylim()
    ax.set_yticks(np.arange(start, end, 60))
    ax.set_yticklabels(list(cmv_timeline.index.strftime('%Y-%m')[::-60]), fontsize=30)
    plt.tick_params(axis='x',which='both', labelbottom='off')
    
    plt.title('CMV Moderator Presence Timeline')
    plt.xlabel('r/ChangeMyView Moderators', fontsize=40)
    plt.ylabel('Date', fontsize=40)
    
    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6])
    colorbar.set_ticklabels(['', 'other perm types',
                             '+ access, posts', '+ access, flair, mail, posts',
                             'all'])
    
    plt.tight_layout()
    plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/cmv-timeline-H.png')



######## RUN SCRIPT

