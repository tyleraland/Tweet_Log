#!/usr/bin/env python
import json
import timestamps
import specials
# Calls timestamp.py to sort
jsfile = '/Users/tal/Code/tweets/data/js/tweets/2013_06.js'
tweets = timestamps.sort_time(jsfile)
specials.process(tweets)
