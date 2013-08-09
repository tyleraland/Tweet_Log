import re
import csv
import pickle

wo = re.compile('([a-zA-Z]*.?[a-zA-Z]+)@? ([\d.\s]+)+')
eat = re.compile('([.a-z]*[a-z]+)(?:\.)?([0-9]*)([a-z]*)')
wolog = csv.writer(open('workout_log.csv','w'), quoting=csv.QUOTE_ALL)
# wolog header
# times: "year monthnumber daynumber hour minute"
# wo_id is shared between sets from the same session
# lifts: "weight1:rep1-rep2-...-repN;weight2:rep1-rep2-..."
wolog.writerow(["start_time","end_time","wo_id","exercise","lifts"])

new_foods = [] # Later written to new food file
newff = open('needs_ids','w') # new food file
ft = open('food_table', 'r')
macro_table = pickle.load(open('macro_table', 'r'))
food_table = pickle.load(ft)
ft.close() # Will re-write file later, so need to close now

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

def consume(text):
    match = re.findall(eat,text)
    for food in match:
        name = food[0]
        if food[1]:
            quantity = food[1]
        else:
            quantity = -1 # Force exception. TODO: Each db_id should have default value
        if food[2]:
            unit = food[2]
        if name in macro_table:
            multi = reduce( lambda a,b: a+b, map( lambda tup: tup[1], macro_table[name]))
            macro = ''
            for tup in macro_table[name]:
                macro += tup[0] + '.' + str(int(tup[1]*multi)) + 'g' + ' '
            consume(macro)
        elif not name in food_table:
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
            consume(tweet[2][3:])
    # save new_foods for later identification
    for food in set(new_foods):
        newff.write("%s\n" % food)
