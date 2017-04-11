#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 17:30:46 2017

@author: emg
"""
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap

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
            {'+access,-config,-flair,-mail,+posts,-wiki':3,
                 '+access,-config,+flair,+mail,+posts,-wiki':4,
                 '+all':5}
            ).fillna(2)
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
  
def date_presence(date, start, end, after, perm_level): 
    '''check mod presence on date'''
    if date >= start and date <= end:
        return float(perm_level)
    elif date > end and date <= after:
        return 1.0
    else:
        return 0.0

def timeline_df(df):
    '''convert moderator instance date to timeline df'''
    timeline = pd.DataFrame(index = list(pd.date_range(start = df['date'].min(),
                                                      end = df['pubdate'].max(),
                                                    freq='D')))
    for name in list(set(df['name'])):
        if list(df['name']).count(name) == 1:
            d = {}
            subset = df.loc[name]
            dates = pd.date_range(start = subset['date'],
                                  end = subset['pubdate'],
                                  freq='D')
            for date in dates:
                d[date] = date_presence(date, subset['date'],
                                         subset['pubdate'], subset['after'],
                                           subset['perm_level'])
            timeline[name] = pd.Series(d)

        elif list(df['name']).count(name) > 1:
            d = {}
            subset = df.loc[name]
            dates = list(pd.date_range(start = subset['date'].min(),
                                                      end = subset['pubdate'].max(),
                                                    freq='D'))
            for row in subset.itertuples():
                for date in dates:
                    start, end, after, perm_level = row[2], row[3], row[4],row[5]
                    presence = date_presence(date, start, end, after, perm_level)
                    if presence > 0:
                        d[date] = presence
            timeline[name] = pd.Series(d)
    timeline.fillna(0, inplace=True)
    timeline = timeline[list(df.sort_values('date')['name'].drop_duplicates())]
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
    colours = ('white','grey','orange','green','red','blue')
    cmap = LinearSegmentedColormap.from_list('Custom', colours, len(colours))
    return cmap

def joint_plot():
    colours = ('white','grey','orange','green','red','blue')
    cmap = LinearSegmentedColormap.from_list('Custom', colours, len(colours))
    
    fig, (ax1, ax2) = plt.subplots(2,1)#, figsize=(25,12)) #, gridspec_kw = {'width_ratios':[2, 1]})
    
    # TD subplot
    g1 = sns.heatmap(weeks1,cmap=cmap,cbar=False,ax=ax1)
    g1.set_title('TD Moderator Timeline')
    g1.set_ylabel('Month')
    g1.set_xlabel('TD Moderators')
    g1.tick_params(axis='x',which='both', labelbottom='off')
    
    # CMV subplot
    g2 = sns.heatmap(weeks2,cmap=cmap,ax=ax2)
    g2.set_title('CMV Moderator Timeline')
    g2.set_ylabel('Month')
    g2.set_xlabel('CMV Moderators')
    g2.tick_params(axis='x',which='both', labelbottom='off')   
    
    # legend
    colorbar = ax2.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.2, 2, 2.8, 3.6, 4.4])
    colorbar.set_ticklabels(['not present', 'possibly present', 'other perm types',
                             '+ access, posts', '+ access, flair, mail, posts',
                             'all'])
    
    plt.gca().set_yticks(plt.gca().get_yticks()[::3])
    plt.tight_layout()
    
    #plt.savefig('/Users/emg/Programming/GitHub/subreddit-visuals/figures/joint-timelines.png')


timeline1 = timeline_df(td_data())
tops = ['OhSnapYouGotServed','Grakmarr']

def td_plot():
    sns.heatmap(weeks1,cmap=cmap,cbar=False)
    plt.title('TD Moderator Timeline')
    plt.ylabel('Month (Quarterly)')
    plt.xlabel('TD Moderators')
    plt.tick_params(axis='x',which='both', labelbottom='off')
    plt.gca().set_yticks(plt.gca().get_yticks()[::20])



def cmv_plot():
    sns.heatmap(weeks2,cmap=cmap,cbar=False)
    plt.title('CMV Moderator Timeline')
    plt.ylabel('Month (Quarterly)')
    plt.xlabel('CMV Moderators')
    plt.tick_params(axis='x',which='both', labelbottom='off')
    #plt.gca().set_yticks(plt.gca().get_yticks()[::3])



######## RUN SCRIPT

timeline1 = timeline_df(td_data())
 
# get monthly timelines     
months1 = monthly_timeline(td_data())
months2 = monthly_timeline(cmv_data())

# get weekl timelines
weeks1 = weekly_timeline(td_data())
weeks2 = weekly_timeline(cmv_data())


# get plots
cmap = set_cmap()
#joint_plot() # saves plot ot file
td_plot()
cmv_plot()

