import re
import csv

wo = re.compile('([a-zA-Z]*.?[a-zA-Z]+)@? ([\d.\s]+)+')
eat = re.compile('([.a-z]*[a-z]+)(?:\.)?([0-9]*)([a-z]*)')
wolog = csv.writer(open('DUMMYCSV.csv','w'), quoting=csv.QUOTE_ALL)
# wolog header
# times: "year monthnumber daynumber hour minute"
# wo_id is shared between sets from the same session
# lifts: "weight1:rep1-rep2-...-repN;weight2:rep1-rep2-..."
wolog.writerow(["start_time","end_time",
                "wo_id","exercise","lifts"])

new_foods = []
food_table = {} # Load from file

def workout(tweet,wo_id):
    text = tweet[2][3:]
    exers = re.findall(wo,text)
    for exer in exers:
        row = []
        row.append(" ".join([str(field) for field in tweet[0].timetuple()[:-4]])) # Start
        row.append(" ".join([str(field) for field in tweet[1].timetuple()[:-4]])) # Stop time
        row.append(wo_id)
        lift_name = exer[0]  # TODO: Use lift_name as key into lift_alias table, use standardized name
        wgroups = exer[1].split() #e.g. ['100.9.8', '120.5.5']
        lifts = '' # See wolog header comment above
        for wgroup in wgroups: #e.g. wogroup = '100.9.8'
            nums = wgroup.split('.')
            if len(lifts) > 0:
                lifts += ';'
            lifts += nums[0] + ':'
            lifts += '-'.join(nums[1:])
        row.extend([lift_name, lifts])
        wolog.writerow(row)

def consume(tweet):
    text = tweet[2][3:]
    match = re.findall(eat,text)
    name = match[0][0]
    if match[0][1]:
        quantity = match[0][1]
    else:
        quantity = -1 # Force breakage.  Each db_id should have default value
    if match[0][2]:
        unit = match[0][2]
    if not name in food_table:
        new_foods.append(name)

def process(tweets):
    wo_id = 1
    for tweet in tweets:
        text = tweet[2]
        clue = text.split()[0]
        if clue == 'wo': # workout
            workout(tweet, wo_id)
            wo_id += 1
        if clue == 'eat': # eat
            consume(tweet)
    # Ask user about new_foods
    for food in new_foods:
        print(food)
    # Save food_table to file
