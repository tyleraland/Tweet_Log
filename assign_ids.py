# Read needs_ids, create set of foods
# foreach food
# - Run %lik% sql query into database, suggest db_id,names
# - Prompt user for db_id

import sqlite3
import pickle
from pprint import pprint
import shutil

# Load foods for assignment
ff = open('needs_ids','r')
items = set(ff.read().splitlines()) # Remove duplicates
ff.close()
# Load food_table, where IDs will be assigned
shutil.copyfile('food_table', 'food_table.backup')
ft = open('food_table','r')
food_table = pickle.load(ft)
ft.close()
# Load sql database, from which IDs will be suggested
conn = sqlite3.connect('/Users/tal/Code/food.db')
c = conn.cursor()
defer = []
given = []

for item in items:
    hits = []
    for word in item.split("."):
        c.execute("select shrt_desc,db_id from food where shrt_desc like ?", ('%'+word+'%',))
        hits.append(set(c.fetchall()))
    shared = reduce(lambda a,b: a&b, hits, hits[0]) # Intersection of all queries
    pprint(shared)
    pprint(item)
    ret = raw_input("Enter db_id [-1 for nonfood], or 'd' to defer, 'x' to quit: ")
    try:
        if ret == 'd': #defer
            defer.append(item)
            print("deferred!")
        elif ret == 'x':
            break
        else: #ret is integer; -1 is nonfood
            food_table[item] = int(ret)
            given.append(item)
    except Exception: print(Exception)
    #pprint.pprint(shared)

ft = open('food_table','w') # Save food_table entries
pickle.dump(food_table,ft)
ft.close()
ff = open('needs_ids','w')
for food in (items - set(given)):
    ff.write("%s\n" % food)
ff.close()
