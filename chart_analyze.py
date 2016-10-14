import sqlite3
import json
import pandas as pd
import numpy as np

conn = sqlite3.connect('police_killings.sqlite')
cur = conn.cursor()

cur.execute('''SELECT DISTINCT * from Deaths''')
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
armed = df['armed']
print armed
#Bar Chart 1
df['race'] = df['race'].replace('Asian/Pacific Islande','Asian').replace('Hispanic/Latino','Hispanic').replace('Native','Native American')
df_grouped = df.groupby(['armed','race']).count().rename(columns = {'age':'count'})['count']
df_grouped = df_grouped.unstack(0)
col_list = list(df_grouped)
for var in ['Firearm','No']:col_list.remove(var)
df_grouped['Other_all'] = df_grouped[col_list].sum(axis=1)
df_grouped = df_grouped.drop(col_list,1).drop(['Other','Unknown','Arab-American'])
df_race_pop = pd.read_csv('pop_race.csv').set_index('race')[['population','pop_mil']]
df_all = df_grouped.join(df_race_pop)
for var in ['Firearm', 'No', 'Other_all']:
    df_all['per_'+var] = df_all[var]/df_all['pop_mil']
df_all['total'] = df_all[['per_Firearm','per_No','per_Other_all']].sum(axis=1)
df_all = df_all[['per_No','per_Firearm','per_Other_all']]
df_all.columns = ['Unarmed', 'Firearm', 'Other/Unknown']
df_all.to_csv('chart1.csv')

#Pie Chart 1
df_totals = df.groupby(['race']).count().rename(columns = {'age':'Total'})
df_totals['race_cat'] = ['Other','Other','Black','Other','Other','Other','Other','White']
df_totals = df_totals[['race_cat','Total']]
df_totals = df_totals.groupby(['race_cat']).sum()
df_totals['All'] = df_totals['Total'].sum()
df_totals['pct'] = df_totals['Total']/df_totals['All']
df_totals.reindex(index = ['White','Black','Other']).to_csv('data/pie1.csv')

#Pie Chart 2
df_armed = df
df_armed['armed'] = df_armed['armed'].replace('Disputed','Other').replace('Knife','Other').replace('Non-lethal firearm','Other').replace('Unknown','Other').replace('Vehicle','Other')
df_armed['race'] = df_armed['race'].replace('Arab-American','Other').replace('Asian','Other').replace('Hispanic','Other').replace('Native American','Other').replace('Unknown','Other')
df_armed = df_armed.groupby(['armed','race'], as_index=False).count().rename(columns = {'age':'Total'})
df_unarmed = df_armed.groupby('armed').get_group('No')[['armed','race','Total']]
df_unarmed['All'] = df_unarmed['Total'].sum()
df_unarmed['pct'] = df_unarmed['Total']/df_unarmed['All']
df_unarmed['race'] = pd.Categorical(df_unarmed['race'], ['White','Black','Other'])
df_unarmed.sort_values('race').to_csv('data/pie2.csv')

#Pie Chart 3
df_firearm = df_armed.groupby('armed').get_group('Firearm')[['armed','race','Total']]
df_firearm['All'] = df_firearm['Total'].sum()
df_firearm['pct'] = df_firearm['Total']/df_firearm['All']
df_firearm['race'] = pd.Categorical(df_firearm['race'], ['White','Black','Other'])
df_firearm.sort_values('race').to_csv('data/pie3.csv')

#Pie Chart 4
df_other = df_armed.groupby('armed').get_group('Other')[['armed','race','Total']]
df_other['All'] = df_other['Total'].sum()
df_other['pct'] = df_other['Total']/df_other['All']
df_other['race'] = pd.Categorical(df_other['race'], ['White','Black','Other'])
#df_other.sort_values('race').to_csv('pie4.csv')

#Demographic Pie Chart
df_demo = df_race_pop
df_demo['race_cat'] = ['White','Black','Other','Other','Other']
df_demo = df_demo[['race_cat','pop_mil']]
df_demo = df_demo.groupby(['race_cat']).sum()
df_demo['All'] = df_demo['pop_mil'].sum()
df_demo['pct'] = df_demo['pop_mil']/df_demo['All']
df_demo.reindex(index = ['White','Black','Other']).to_csv('data/pie4.csv')
print df_demo

#Time series

df['race'].loc[~df['race'].isin(['White','Black'])] = 'Other'
df['armed1'] = armed
print df
#df['armed'].loc[~df['armed'].isin(['Firearm','No'])] = 'Unknown'
dates = df['date'].str.split(' ', expand = True)
df['date'] = pd.to_datetime(df['date'])
df['month'] = dates[0]
df['year'] = dates[2]
df['ym'] = df['date'].map(lambda x: 1000*x.year + x.month)
ts_race = df.groupby(['ym', 'year', 'month', 'race']).count().rename(columns = {'age':'count'})['count'].unstack().fillna(0)
ts_armed = df.groupby(['ym', 'year', 'month', 'armed']).count().rename(columns = {'age':'count'})['count'].unstack().fillna(0)
print ts_armed
ts_race.to_csv('data/ts_race.csv')
ts_armed.to_csv('data/ts_armed.csv')
