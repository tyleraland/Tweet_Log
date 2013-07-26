# Read needs_ids, create set of foods
# foreach food
# - Run %lik% sql query into database, suggest db_id,names
# - Prompt user for db_id or 'x'

import sqlite3

conn = sqlite3.connect('/Users/tal/Code/food.db')
c = conn.cursor()
item = 'choc.milk'
#for word in item.split("."):

hits = []
for word in item.split("."):
    c.execute("select shrt_desc,db_id from food where shrt_desc like ?", ('%'+word+'%',))
    hits.append(set(c.fetchall()))
shared = reduce(lambda a,b: a&b, hits, hits[0]) # Intersection of three queries

#q = c.execute("select shrt_desc,db_id from food where shrt_desc like '%milk%'")
#f = open('needs_ids','r').readlines()
#for line in f:
#    print(line.rstrip()) # Remove pesky newlines
