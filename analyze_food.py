import csv
import sqlite3
import numpy
from numpy import array
from pprint import pprint
from datetime import datetime

food_log = open('food_log.csv','r')
food = csv.reader(food_log)
#Header: time,text,db_id,quantity,unit

conn = sqlite3.connect("/Users/tal/Code/food.db")
c = conn.cursor()
food.next() # Discard header

# Indices for common nutrients (starting at 0):
# Adjusted protein: 52
# Carbohydrate    : 63
# Fiber           : 78
# Fat, total      : 125
# MUFA            : 72
# PUFA            : 73
# SFA             : 74
# Trans-fats      : 75,76,77
# Omega-3 FAs:
# - 18:3 n-3 / Alpha-linolenic: 25
# - 20:3 n-3                  : 33 
# - 20:5 n-3 / EPA            : 38
# - 22:5 n-3 / DPA            : 45
# - 22:6 n-3 / DHA            : 46
# Omega-6 FAs
# - 18:2 n-6 cis,cis                      : 21
# - 18:3 n-6 cis,cis,cis / Gamma-linolenic: 26
# - 20:2 n-6 cis,cis / eicosadienoic      : 32
# - 20:3 n-6                              : 34
# - 20:4 n-6                              : 36

for line in food:
    #print(line[1],line[2],line[3]) #text,db_id, quantity
    dt = line[0].split()
    date = dt[0].split('-')
    #time = datetime[1]
    date = datetime(int(date[0]), int(date[1]), int(date[2]))
    c.execute("SELECT * FROM food WHERE db_id=?", (line[2],))
    nuts = array(c.fetchone())
    desc = nuts[0]
    nuts[0] = 0.0 # Replace shrt_desc (name) with dummy float value
    nuts = map( lambda x: 0 if x=='NA' else x, nuts) # Replaces 'NA' with 0
    nuts = array(nuts).astype(float)
    mult = float(line[3]) / 100.0
    nuts *= mult
    print("Carbs: " + str(nuts[63]))
    print("Protein: " + str(nuts[52]))
    print("Fat: " + str(nuts[125]))
    break
