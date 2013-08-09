#!/usr/bin/env python
import json
import timestamps
import specials
# Calls timestamp.py to sort
files = ['2012_10', '2012_11', '2012_12', 
                    '2013_02', '2013_03', '2013_04', '2013_05', '2013_06',
         '2013_07', '2013_08']
jstemp = '/Users/tal/Code/tweets/data/js/tweets/'
for jsfile in files:
    tweets = timestamps.sort_time(jstemp + jsfile + '.js')
    specials.process(tweets)
