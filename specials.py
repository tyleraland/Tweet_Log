import re
import csv
import pickle
from pprint import pprint

wo = re.compile('([a-zA-Z]*.?[a-zA-Z]+)@? ([\d.\s]+)+')
eat = re.compile('([.a-z]*[a-z]+)(?:\.)?([0-9]*)([a-z]*)')
wolog = csv.writer(open('workout_log.csv','w'), quoting=csv.QUOTE_ALL)
# wolog header
# times: "year monthnumber daynumber hour minute"
# wo_id is shared between sets from the same session
# lifts: "weight1:rep1-rep2-...-repN;weight2:rep1-rep2-..."
wolog.writerow(["start_time","end_time","wo_id","exercise","lifts"])

foodlog = csv.writer(open('food_log.csv','w'), quoting=csv.QUOTE_ALL)
foodlog.writerow(["time","text","db_id","quantity","units"])

new_foods = [] # Later written to new food file
newff = open('needs_ids','w') # new food file
ft = open('food_table', 'r')
macro_table = pickle.load(open('macro_table', 'r'))
food_table = pickle.load(ft)
ft.close() # Will re-write file later, so need to close now

# Multiplier; number of units in 100 grams
conv_table = {'oz':28.0, 'shot':28.0, 'g':1.0, 'mg':.001, 'kg':1000, 'f':1.0} 
servings = {'egg':(50,'g'), 'vitad':(1000,'IU'), 'coil':(10,'g'), 'ooil':(10,'g'),
           'lard':(10,'g'), 'mct':(10,'g'), 'butr':(10,'g'), 'butter':(10,'g'), 'tallow':(10,'g'),
            'koil':(1,'mg'), 'nyeast':(10,'g'), 'whey':(30,'g'), 'iodine':(1,'mcg'),
            'cinna':(500,'mg'), 'thyme':(500,'mg'), 'curryp':(500,'mg'),'crm':(15,'g'),
            'bouillon':(1,'g'),'paprika':(250,'mg'), 'turmeric':(200,'mg'),'oregano':(200,'mg'),
            'cumin':(250,'mg')} 

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

def consume(start, text):
    match = re.findall(eat,text)
    for food in match: # food = name[,quantity[,units]]
        unit = ''
        name = food[0]
        # Check if foodname is a macro for several foods
        # Determine multiplier to scale macro by
        if name in macro_table:
            if food[1]: # If quantity provided, grab it
                quantity = int(food[1])
                if food[2]: 
                    unit = food[2]
                if unit in conv_table:
                    quantity *= conv_table[unit]
                    unit = 'g'
                    multi = quantity / reduce( lambda a,b: a+b, map( lambda tup: tup[1] if len(tup) > 1 else 0,  macro_table[name]))
                elif unit == '':
                    multi = quantity
            else:
                multi = 1
            macro = ''
            for tup in macro_table[name]:
                if len(tup) > 1:
                    macro += tup[0] + '.' + str(int(tup[1]*multi)) + 'g' + ' '
                else:
                    macro += tup[0] + ' '
            #print(macro)
            consume(start, macro)
            continue
        if food[1]:
            quantity = int(food[1])
        else:
            quantity = 1
        if food[2]:
            unit = food[2]
        # If units are omitted (e.g. fish.3) there are several interpretations:
        # Item may have unique unit/quantity in servings table
        # Otherwise, if quantity <= 16 assume quantity is ounces
        # If larger quantity (e.g. fish.200), assume grams
        if not unit:
            if name in servings:
                quantity *= servings[name][0]
                unit = servings[name][1]
            elif quantity <= 16:
                unit = 'oz'
            else:
                unit = 'g'
        if unit in conv_table:
            quantity *= conv_table[unit]
            unit = 'g'
        else: #TODO: handle weird units
            pass
            #print("WHAT TO DO WITH UNIT " + unit + " ????") # Others: mcg, IU ... nonfood units
        if not name in food_table:
            new_foods.append(name)
        elif food_table[name] > 0: # food item
            foodlog.writerow([start,name,food_table[name],int(quantity),unit])
        else: #TODO
            pass #nonfood item

def process(tweets):
    wo_id = 1
    for tweet in tweets:
        start = tweet[0]
        stop = tweet[1]
        text = tweet[2]
        clue = text.split()[0]
        if clue == 'wo': # workout
            workout(tweet, wo_id)
            wo_id += 1
        if clue == 'eat': # eat
            consume(start, tweet[2][3:].lower())
    # save new_foods for later identification
    for food in set(new_foods):
        newff.write("%s\n" % food)
