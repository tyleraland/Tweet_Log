import re
import csv

wo = re.compile('([a-zA-Z]*.?[a-zA-Z]+)@? ([\d.\s]+)+')
wolog = csv.writer(open('DUMMYCSV.csv','w'), quoting=csv.QUOTE_ALL)
wolog.writerow(["start_time","end_time",
                "wo_id","exercise","lifts"]) # Header

def workout(tweet,wo_id):
    text = tweet[2][3:]
    exers = re.findall(wo,text)
    for exer in exers:
        row = []
        row.append(" ".join([str(field) for field in tweet[0]])) # Start time
        row.append(" ".join([str(field) for field in tweet[1]])) # Stop time
        row.append(wo_id)
        lift_name = exer[0]
        wgroups = exer[1].split() #e.g. ['100.9.8', '120.5.5']
        lifts = '' #later: weight:rep1-rep2-rep3;weight:rep1-rep2"
        for wgroup in wgroups: #e.g. '100.9.8'
            nums = wgroup.split('.')
            if len(lifts) > 0:
                lifts += ';'
            lifts += nums[0] + ':'
            lifts += '-'.join(nums[1:])
        row.extend([lift_name, lifts])
        wolog.writerow(row)

def process(tweets):
    wo_id = 1
    for tweet in tweets:
        text = tweet[2]
        clue = text.split()[0]
        if clue == 'wo': # workout
            workout(tweet, wo_id)
            wo_id += 1
