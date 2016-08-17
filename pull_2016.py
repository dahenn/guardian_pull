from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import sqlite3

# Create SQLite Database
conn = sqlite3.connect('police_killings.sqlite')
cur = conn.cursor()

# Initialize data and drivers, navigate to 2016 page
rows = list()
driver = webdriver.Chrome()
driver.implicitly_wait(15)
driver.get("http://www.theguardian.com/us-news/ng-interactive/2015/jun/01/the-counted-police-killings-us-database")
ac1 = ActionChains(driver)
ac2 = ActionChains(driver)
ac3 = ActionChains(driver)
ac4 = ActionChains(driver)
ac5 = ActionChains(driver)

# Scroll up and down the page in order to load all cells
time.sleep(2)
for j in range(5):
    ac1.key_down(Keys.PAGE_DOWN).perform()
    time.sleep(0.5)
    ac2.key_up(Keys.PAGE_DOWN).perform()
time.sleep(1)
for j in range(5):
    ac3.key_down(Keys.PAGE_UP).perform()
    time.sleep(0.25)
    ac4.key_up(Keys.PAGE_UP).perform()
time.sleep(1)

# Go through each month and each listing, skipping odd 'months' that erroneously appear and are empty
months = driver.find_elements_by_css_selector('div.month')
i=1
for month in months:
    # print "@@@@@@@@@@@@@@@@", i, "@@@@@@@@@@@@@@@@"
    if (i % 2 == 0):
        i = i + 1
        continue
    else:
        records = month.find_elements_by_css_selector('article.incident')
        for x in records:
            link = x.find_element_by_css_selector('div.record')
            # Ugly try-except statements to try to get this to run quicker
            try:
                time.sleep(0.5)
                link.click()
            except:
                try:
                    time.sleep(1)
                    link.click()
                except:
                    try:
                        time.sleep(1.5)
                        link.click()
                    except:
                        try:
                            time.sleep(2)
                            link.click()
                        except:
                            close.click()
                            time.sleep(10)
                            link.click()
            try:
                time.sleep(0.5)
                details = driver.find_element_by_css_selector('article.details-container')
                info = details.text.split('\n')
                date = info[0]
                name = info[1]
            except:
                try:
                    time.sleep(1)
                    details = driver.find_element_by_css_selector('article.details-container')
                    info = details.text.split('\n')
                    date = info[0]
                    name = info[1]
                except:
                    try:
                        time.sleep(2.5)
                        details = driver.find_element_by_css_selector('article.details-container')
                        info = details.text.split('\n')
                        date = info[0]
                        name = info[1]
                    except:
                        time.sleep(10)
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
            print "Pass", date
            e = (date, name, race, sex, age, address, city, state, armed, cause, department)
            container = details.find_element_by_css_selector("div.details")
            close = details.find_element_by_css_selector("div.close")
            try:
                container.click()
            except:
                time.sleep(1)
                container.click()
            close.click()
            rows.append(e)
            cur.execute('INSERT OR IGNORE INTO Deaths VALUES (?,?,?,?,?,?,?,?,?,?,?)', e )
            conn.commit()
        i = i+1
driver.close()
conn.commit()
cur.close()
