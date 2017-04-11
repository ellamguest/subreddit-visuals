 #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 15:46:10 2017

@author: emg
"""

import pandas as pd
#from create_mod_timeline import *
#import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap

#sns.set_style("white") # set aes to white w/out grid

## IMPORT DATA and MAKE MONTHLY TIMELINE
# CMV data
def cmv_data():
    df = pd.read_csv('/Users/emg/Programming/GitHub/cmv/tidy_data/dated_mod_df.csv', index_col=0)
    df['date'] = pd.to_datetime(df['date'])
    df['pubdate'] = pd.to_datetime(df['pubdate'].astype(str), format='%Y%m%d%H%M%S')
    df['perm_level'] = df['permissions'].map(
            {'+access,-config,-flair,-mail,+posts,-wiki':3,
                 '+access,-config,+flair,+mail,+posts,-wiki':4,
                 '+all':5}
            ).fillna(2)
    return df

# TD data
def td_data():
    df = pd.read_csv('/Users/emg/Programming/GitHub/subreddit-visuals/tidy_data/mods/td-mod-hist.csv', index_col=0)
    df['perm_level'] = df['permissions'].map(
            {'+access,-config,-flair,-mail,+posts,-wiki':3,
                 '+access,-config,+flair,+mail,+posts,-wiki':4,
                 '+all':5}
            ).fillna(2)
    return df



## CREATE MONTHLY TIMELINES
df1 = td_data() 
timeline = timeline_df(df1)
months1 = monthly_timeline(df1)

df2 = cmv_data() 
months2 = monthly_timeline(df2)
timeline2 = timeline_df(df2)


##BETTER COLOURED PLOT
#set colormap


# when right censoring boundary = 0.5


def plot():
    colours = ('white','grey','orange','green','red','blue')
    cmap = LinearSegmentedColormap.from_list('Custom', colours, len(colours))
    
    fig, (ax1, ax2) = plt.subplots(1,2, figsize=(25,12)) #, gridspec_kw = {'width_ratios':[2, 1]})
    
    # TD subplot
    g1 = sns.heatmap(months1,cmap=cmap,cbar=False,ax=ax1)
    g1.set_title('TD Moderator Timeline')
    g1.set_ylabel('Month')
    g1.set_xlabel('TD Moderators')
    g1.tick_params(axis='x',which='both', labelbottom='off')
    
    # CMV subplot
    g2 = sns.heatmap(months2,cmap=cmap,ax=ax2)
    g2.set_title('CMV Moderator Timeline')
    g2.set_ylabel('Month')
    g2.set_xlabel('CMV Moderators')
    g2.tick_params(axis='x',which='both', labelbottom='off')   
    
    # legend
    colorbar = ax2.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6])
    colorbar.set_ticklabels(['not present', 'possibly present', 'other perm types',
                             '+ access, posts', '+ access, flair, mail, posts',
                             'all'])
    
    plt.gca().set_yticks(plt.gca().get_yticks()[::3])
    plt.tight_layout()
    
    plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/joint-timelines.png')

plot()

def td_plot():
    #td plot only
    sns.heatmap(months1,cmap=cmap,cbar=False)
    plt.title('TD Moderator Timeline')
    plt.ylabel('Month (Quarterly)')
    plt.xlabel('TD Moderators')
    plt.tick_params(axis='x',which='both', labelbottom='off')
    #plt.gca().set_yticks(plt.gca().get_yticks()[::3])

td_plot()

def cmv_plot():
    #cmv plot only
    sns.heatmap(months2,cmap=cmap,cbar=False)
    plt.title('CMV Moderator Timeline')
    plt.ylabel('Month (Quarterly)')
    plt.xlabel('CMV Moderators')
    plt.tick_params(axis='x',which='both', labelbottom='off')
    #plt.gca().set_yticks(plt.gca().get_yticks()[::3])

cmv_plot()

