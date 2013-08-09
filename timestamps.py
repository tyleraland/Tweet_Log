import json
import re
import calendar
import datetime

# Dictionary of {'three-letter-month-string':month-number}
months = calendar.month_abbr[1:]
month_num = {months[i]:i+1 for i in range(0,12)}
timestamp = re.compile('\$(\d+).?(\d+)?') # User-inputted timestamp

# Fixdate, takes input date string and moves it by 'offset' minutes (military)
# Eg: date="1 Jan 1990 100", offset="-200" -> "31 Dec 1989 2300"
def fixdate(date, dayoff, hroff):
    delta = datetime.timedelta(0,0,dayoff,hroff)
    return date + delta

# Return list of [start_time, stop_time, text] sorted by start_time
def sort_time(jsfile):
    f = open(jsfile, 'r')
    f.readline()                # Remove useless line
    data = json.loads(f.read()) # List of tweets; each tweet is a dict
    data.reverse()              # Now in submitted-chronological order
    tweets = []
    for tweet in data:
        text = tweet["text"].lower()
        time = tweet["created_at"]   # default timestamp
        time = str(time).split()[1:]
        #datetime - year, month, day, hour, minute
        time = datetime.datetime(int(time[4]), month_num[time[0]], int(time[1]),
                                 int(time[2][0:2]), int(time[2][3:5]))
        # Subtract 7 hours from UTC time to give west coast time
        # TODO: daylight savings
        time = fixdate(time, 0, -7)
        try: # Try to match a regex timestamp pattern
            match = re.search(timestamp, text) # matches $100.200
            ss = match.groups() # Assume a successful match
            if len(ss[0]) <= 2: # minutes omitted, like $9
                start = time.replace(hour=int(ss[0]))
            else:
                start = time.replace(hour=int(ss[0][:-2]), minute=int(ss[0][-2:]))
            if ss[1]:
                if len(ss[1]) <= 2: # minutes omitted
                    stop = time.replace(hour=int(ss[1]))
                else:
                    stop = time.replace(hour=int(ss[1][:-2]), minute=int(ss[1][-2:]))
            else:
                stop = start
        except Exception: # Timestamp omitted or malformed; ValueError/AttributeError
            start = time
            stop = time
        if start > time: # If user-inputted timestamp is LATER than default timestamp
            start = fixdate(start, -1, 0) # Then it's from yesterday
            stop = fixdate(stop, -1, 0)
        # Excise timestamp from the text
        tweets.append([start,stop,str(text)])
        # sort first on start time, then on day
    tweets.sort(key=lambda triple: 100*triple[0].hour + triple[0].minute)
    tweets.sort(key=lambda triple: 100*triple[0].day)
    return tweets

