#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 17:30:46 2017

@author: emg
"""
import pandas as pd

def prep_df(df):
    #subset df into required coluns and types
    subset = (df[['name', 'date', 'pubdate', 'perm_level']].copy()
                .assign(
                    date=lambda df: df['date'].pipe(pd.to_datetime).dt.normalize(),
                    pubdate=lambda df: df['pubdate'].pipe(pd.to_datetime).dt.normalize()))


    subset = subset.drop_duplicates(['name','date'], keep='last')
    subset.set_index('name', inplace=True, drop=False)
    return subset

# list of dates
def date_range(df):
    # get list of days between first mod 'date' and last 'pubdate'
    start = df['date'].min()
    end = df['pubdate'].max()
    dates = list(pd.date_range(start, end, freq='D'))
    return dates

def date_list(dates, start, end, perm_level=0):
    # return a boolean list of presence for the dates range
    # default values 1 unless perm_level given
    dl = []
    for date in dates:
            if date > start and date <= end:
                dl.append(perm_level)
            else:
                dl.append(0)
    return dl

def check_repeats(df):
    # check in name has multiple mod instance
    count = df['name'].value_counts()
    repeats = list(count[count>1].index)
    return repeats

def timeline_dict(df, names, dates):
    #list of names must have no repeat mods
    # df has names as index and columns 'date' and 'pubdate
    d = {}
    repeats = check_repeats(df)
    for name in names:
        if name not in repeats:
            info = date_list(dates,
                             start=df.loc[name]['date'],
                             end=df.loc[name]['pubdate'],
                             perm_level=df.loc[name]['perm_level'])
            d[name] = info
        else:
            data =  df.loc[name]
            lines = []
            for row in data.itertuples():
                start, end, perm_level = row[2], row[3], row[4]
                line = date_list(dates, start, end, perm_level)
                lines.append(line)
            info = [x + y for x, y in zip(lines[0],lines[1])]
            d[name] = info
    return d

def timeline_df(df):
    #df should have columns name date, pubdate, perm_level
    # df index should be qual to names
    subset = prep_df(df)
    names = list(subset.sort_values('date')['name'].drop_duplicates())
    dates = date_range(subset)
    t_dict = timeline_dict(subset, names, dates)
    timeline = pd.DataFrame.from_dict(t_dict)
    timeline.index = dates
    temps = timeline.sum()[timeline.sum()==0].index #remove mods present less than a week
    timeline = timeline[[name for name in names if name not in temps]] #over mods by time of first modding
    return timeline
    