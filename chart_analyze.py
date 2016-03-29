import sqlite3
import json
import pandas as pd
import numpy as np

conn = sqlite3.connect('police_killings.sqlite')
cur = conn.cursor()

cur.execute('''SELECT * from Deaths''')
data = cur.fetchall()
index = range(1,len(data))
date = ()
name = ()
race = ()
sex = ()
age = ()
state = ()
armed = ()
for row in data:
    date = (row[0],) + date
    name = (row[1],) + name
    race = (row[2],) + race
    sex = (row[3],) + sex
    age = (row[4],) + age
    state = (row[7],) + state
    armed = (row[8],) + armed
data_dict = {'date':date, 'name':name, 'race':race, 'sex':sex, 'age':age, 'state':state, 'armed':armed}

df = pd.DataFrame.from_dict(data_dict)
df['race'] = df['race'].replace('Asian/Pacific Islande','Asian').replace('Hispanic/Latino','Hispanic')
df_grouped = df.groupby(['armed','race']).count().rename(columns = {'age':'count'})['count']
df_grouped = df_grouped.unstack(0)
col_list = list(df_grouped)
for var in ['Firearm','No']:col_list.remove(var)
df_grouped['Other_all'] = df_grouped[col_list].sum(axis=1)
df_grouped = df_grouped.drop(col_list,1).drop(['Other','Unknown','Arab-American'])
df_race_pop = pd.read_csv('pop_race.csv').set_index('race')[['population','pop_mil']]
df_all = df_grouped.join(df_race_pop)
print df_all
