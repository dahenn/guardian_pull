import urllib
import sqlite3
import json
import time
import ssl
import re
import pandas as pd

serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"

scontext = None

conn = sqlite3.connect('police_killings.sqlite')
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS Locations
    (date TEXT,
    name TEXT,
    race TEXT,
    sex TEXT,
    armed TEXT,
    cause TEXT,
    lat REAL,
    long REAL,
    date_index INT,
    UNIQUE(name, lat, long, date))''')
cur.execute('SELECT DISTINCT date_index, date from Locations')
data = cur.fetchall()
date_key = {}
for index, date in data:
    date_key[index] = date
print date_key
with open('date_key.json', 'w') as outfile:
    json.dump(date_key, outfile)

cur.execute('''
CREATE TABLE IF NOT EXISTS Deaths_Indexed
    (date TEXT,
    name TEXT,
    address TEXT,
    state TEXT,
    city TEXT,
    race TEXT,
    sex TEXT,
    armed TEXT,
    cause TEXT,
    date_text TEXT,
    UNIQUE(name, address, date))''')

cur.execute('''SELECT date, name, address, state, city, race, sex, armed, cause from Deaths''')
data = cur.fetchall()
months = {'JANUARY':'01', 'FEBRUARY':'02', 'MARCH':'03', 'APRIL':'04', 'MAY': '05', 'JUNE':'06', 'JULY':'07', 'AUGUST':'08', 'SEPTEMBER':'09', 'OCTOBER':'10', 'NOVEMBER':'11', 'DECEMBER':'12'}
for row in data:
    datesplit = row[0].split()
    month = months[datesplit[0]]
    year = datesplit[2]
    day = datesplit[1][:-1]
    if len(day)==1:
        day = "0" + datesplit[1][:-1]
    date = year + '-' + month + '-' + day
    cur.execute('''INSERT OR IGNORE INTO Deaths_Indexed (date, name, address, state, city, race, sex, armed, cause, date_text)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', ( date, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0]) )
    conn.commit()
    print date

cur.execute('''SELECT date_text, name, address, state, city, race, sex, armed, cause from Deaths_Indexed order by date(date)''')
data = cur.fetchall()
_date = "JANUARY 1, 2015"
date_index=1
for row in data:
    if _date != row[0]:
        date_index = date_index + 1
    _date = row[0]
    _name = row[1]
    _race = row[5]
    _sex = row[6]
    _armed = row[7]
    _cause = row[8]
    cur.execute('''SELECT * from Locations
    where date=:_date and name=:_name and race=:_race and sex=:_sex and armed=:_armed and cause=:_cause''', {"_date": _date, "_name": _name, "_race": _race, "_sex": _sex, "_armed": _armed, "_cause": _cause})
    try:
        data = cur.fetchone()[0]
        print "Found in database "
        continue
    except:
        pass
    full_address = row[2] + " " + row[4] + " " + row[3]
    print 'Resolving', full_address
    try:
        url = serviceurl + urllib.urlencode({"sensor":"false", "address": full_address})
        print 'Retrieving', url
        uh = urllib.urlopen(url, context=scontext)
        read = uh.read()
        js = json.loads(str(read))
        # print json.dumps(js, indent=4, sort_keys=True)  # We print in case unicode causes an error
        lat = float(js["results"][0]["geometry"]["location"]["lat"])
        lng = float(js["results"][0]["geometry"]["location"]["lng"])
    except:
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') :
        print '==== Failure To Retrieve ===='
        print read
        break

    cur.execute('''INSERT OR IGNORE INTO Locations (date, name, race, sex, armed, cause, lat, long, date_index)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)''', ( row[0], row[1], row[5], row[6], row[7], row[8], lat, lng, date_index) )
    conn.commit()
    time.sleep(1)
cur.execute('''SELECT date, name, race, sex, armed, cause, lat, long, date_index from Locations''')
data = cur.fetchall()
features = list()
for row in data:
    feature = {'date': row[0], 'name': row[1], 'race': row[2], 'sex': row[3], 'armed': row[4], 'cause': row[5], 'lat': row[6], 'long': row[7], 'date_index': row[8] }
    # print "Lat: ",row[5],"\t", "Long: ",row[6]
    features.append(feature)
df = pd.DataFrame(features)
df['race'].loc[~df['race'].isin(['White','Black'])] = 'Other'
df['armed'].loc[~df['armed'].isin(['Firearm','No'])] = 'Unknown'
features = df.to_dict('records')
with open('event_points1.json', 'w') as outfile:
    json.dump(features, outfile)
print "Data Written"
