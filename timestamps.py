import json
import re
import calendar

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_info = {'Jan':(0,31),'Feb':(1,28),'Mar':(2,31),'Apr':(3,30),'May':(4,31),
              'Jun':(5,30),'Jul':(6,31),'Aug':(7,31),'Sep':(8,30),'Oct':(9,31),
              'Nov':(10,30),'Dec':(11,31)}

def sort_time(jsfile):
    f = open(jsfile, 'r')
    f.readline()                # Remove useless line
    data = json.loads(f.read()) # List of Tweets; each tweet is a dict
    data.reverse()              # Now in submitted-chronological order
    # Pass 1: Create list of [start_time, stop_time, text] and sort by start_time
    tweets = []
    timestamp = re.compile('\$(\d+).?(\d+)?') # User-inputted timestamp
    for tweet in data:
        text = tweet["text"].lower()
        time = tweet["created_at"]   # default timestamp
        time = time.split()
        time = [str(time[1]),int(time[2]),int(time[3][:2]+time[3][3:5]),int(time[5])] #Month,Day,HourMinute,Year
        # Subtract 7 hours from UTC time to give west coast time
        time[2] -= 700
        if time[2] < 0: # Back to yesterday
            time[2] %= 2400
            time[1] -= 1
            if time[1] < 1: # Back to last month
                time[0] = months[month_info[time[0]][0]-1 % 12]
                time[1] = month_info[time[0]][1] # Days in last month
                if time[0] == 'Dec': # Back to last year
                    time[3] -= 1
                if calendar.isleap(time[3]):
                    time[1] += 1
        match = re.search(timestamp, text)
        if match:
            start_stop = match.groups()
        else:
            start_stop = []
        sst = []
        # Check for user-inputted start/stop timestamp.
        # Is it from earlier today? or yesterday, <24 hours ago?
        # Ignore gregorian calendar idiosyncracies (e.g. day=0)
        if len(start_stop) > 0: # User-inputted at least start timestamp
            dtime = int(time[2])
            utime = int(start_stop[0])
            if utime > dtime: # Timestamp is for yesterday
                day = int(time[1]) - 1
            else:
                day = int(time[1])
            sst.append((time[0],day,utime,time[3]))
            if start_stop[1] != None: # User-inputed end timestamp
                dtime = int(time[2])
                utime = int(start_stop[1])
                if utime > dtime: # Timestamp is for yesterday
                    day = int(time[1]) - 1
                else:
                    day = int(time[1])
                sst.append([time[0],day,utime,time[3]])
            else: # End timestamp defaults to start timestamp
                sst.append(sst[0])
        else:     # If neither start nor stop timestamp provided
            sst.append(time) # start
            sst.append(time) # stop
        # Excise timestamp from the text
        if match:
            text = text[:match.start()-1] + text[match.end():]
        sst.append(str(text))
        tweets.append(sst)
    # sort first on time, then on day
    tweets.sort(key=lambda triple: int(triple[0][2]))
    tweets.sort(key=lambda triple: int(triple[0][1]))
    return tweets
