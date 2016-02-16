from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import sqlite3

conn = sqlite3.connect('police_killings.sqlite')
cur = conn.cursor()
cur.execute('''DROP TABLE IF EXISTS Deaths''')
cur.execute('''CREATE TABLE Deaths
    (date TEXT, name TEXT, race TEXT,
     sex TEXT, age INTEGER, address TEXT,
     city TEXT, state TEXT, armed TEXT,
     cause TEXT, department TEXT)''')

rows = list()
driver = webdriver.Chrome()
driver.get("http://www.theguardian.com/us-news/ng-interactive/2015/jun/01/the-counted-police-killings-us-database")

driver.implicitly_wait(10)
button_2015 = driver.find_element_by_xpath('html/body/figure/div[2]/div[2]/div[1]/div[1]/a[2]')
button_2015.click()

records = driver.find_elements_by_css_selector('article.incident')
for record in records:
    link = record.find_element_by_css_selector('div.record')
    time.sleep(0.75)
    driver.implicitly_wait(500)
    link.click()
    time.sleep(1.5)
    driver.implicitly_wait(500)
    details = driver.find_element_by_css_selector('article.details-container')
    info = details.text.split('\n')
    date = info[0]
    name = info[1]
    if info[14].startswith('STATUS'): short = 0
    else: short = 1
    if info[3].startswith('Asian/Pacific'):
        race = info[3][:21]
        sex = info[3][23:].split(',')[0]
    else:
        race = info[3].split(' ')[0]
        sex = info[3].split(' ')[1][:-1]
    try:
        age = int(info[3].split(',')[1])
    except:
        age = -1
    if short==1:
        address = "Unknown"
        city = info[5].split(',')[0]
        state = info[5].split(',')[1].strip()
        armed = info[7]
        cause = info[9]
        department = info[11]
    else:
        address = info[5]
        city = info[6].split(',')[0]
        state = info[6].split(',')[1].strip()
        armed = info[8]
        cause = info[10]
        department = info[12]
    print date, name, race, sex, age, address, city, state, armed, cause, department
    e = (date, name, race, sex, age, address, city, state, armed, cause, department)
    close = details.find_element_by_css_selector('div.close')
    close1 = driver.find_element_by_css_selector('article.incident.visible.highlighted')
    bg = driver.find_element_by_css_selector('modal-background.modal-bg')
    ac = ActionChains(driver)
    driver.implicitly_wait(20)
    ac.move_to_element(close1).move_by_offset(0,25).click(close1).perform()
    rows.append(e)
driver.close()
cur.executemany('INSERT INTO Deaths VALUES (?,?,?,?,?,?,?,?,?,?,?)', rows )
conn.commit()
cur.close()
