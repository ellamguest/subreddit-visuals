# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 10:25:16 2017

@author: emg
"""
import configparser

# CREATE PRAW.INI FILE
config = configparser.ConfigParser()
config['DEFAULT'] = {'client_id' : 'ExUpHR9g1oaTSw', 
                    'client_secret' : 'LBljQWDXxBwfaE-4K-Vy2HuzAWg',
                    'user_agent' : 'why_ask_reddit 1.0'}
with open('praw.ini', 'w') as configfile:
    config.write(configfile)
    
  
# OPEN PRAW.INI FILE
def get_params():
    config = configparser.ConfigParser()
    config.sections()
    config.read('praw.ini')
    return config['DEFAULT']