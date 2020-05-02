#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 00:18:10 2017

@author: caldas
"""

# !/usr/bin/env python3

"""
Created on Sat Aug 12 20:26:40 2017

@author: caldas
"""
# from selenium import webdriver
# driver = webdriver.Firefox(executable_path = '/usr/local/bin/geckodriver')
#
# url = "https://www.youraddress.com"
#
# driver.execute_script("window.open(url,"_self");")  <--- JAVASCRIPT!
# ("window.open('');")


from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime as dt
import pandas as pd

# Creating dataframe to save data.
columns = ["date", "coin", "value", "actual_value", "running_balance", "status", "wallet_hash"]
col_names_payout = ['total', 'paid', 'balance', 'last payment', 'last payout']

df = pd.DataFrame(columns=columns)

# url = "https://www.genesis-mining.com/transactions/index/page"
# driver = webdriver.Firefox(executable_path = '/usr/local/bin/geckodriver')
# driver.get("https://www.genesis-mining.com/en")

with open("test.genesis-balance.html", 'rb') as fp:
    soup = BeautifulSoup(fp, 'html.parser')


def append_data(soup, df):
    transactions = soup.find("div", {"id": "my-transactions"})
    table = transactions.find('table', attrs={'class': 'dash'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    print(len(rows))
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]

        actual_value = 'N/A'
        running_balance = 'N/A'
        try:
            balance_status = row.find('td', attrs={'data-label': 'Status'}).find('span', attrs={'class': 'icon-box'})[
                'data-title']
            start_find_str = cols[1] + ' mining, '
            start_pos = balance_status.find(start_find_str) + len(start_find_str)
            end_pos = balance_status.find(' added to balance.')
            actual_value = balance_status[start_pos: end_pos]

            start_find_str = 'Total Balance: '
            start_pos = balance_status.find(start_find_str) + len(start_find_str)
            end_pos = balance_status.find(' ' + cols[1] + '. ')
            running_balance = balance_status[start_pos: end_pos]
        except:
            print("Status is not defined")

        df = df.append({
            'date': cols[0],
            'coin': cols[1],
            'value': cols[2][:10],
            'actual_value': actual_value,
            'running_balance': running_balance,
            'status': cols[3],
            'wallet_hash': cols[4]
        }, ignore_index=True)
    return df


# try:
#    element = WebDriverWait(driver, 100).until(
#        EC.presence_of_element_located((By.ID, "current-mining"))
#    )
# finally:
# Get number of pages to loop through
print("Parsing page %s." % 1)
# driver.get(url+str(1))
# source = driver.page_source.encode('utf-8')
# soup = BeautifulSoup(source, 'html.parser')


df = append_data(soup, df)

# driver.quit()

### Working on Dataframe

df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
# df['date'] = df['date'].apply(lambda x: dt.datetime.strftime(x, '%m-%d-%Y'))

# df.paid = df.paid.apply(lambda x: True if x == "View Transaction" else False)

# Get all coins
my_coins = df.coin.unique()
print(my_coins)
df = df.sort_values(by=['date'])
balance_start_date = min(df.date)
print(df)
print(balance_start_date)
print('----------------------')

# Create a new dataframe
missing_dates = pd.DataFrame(columns=columns)

row_iterator = df.iterrows()
_, last = next(row_iterator)  # take first item from row_iterator
for i, row in row_iterator:
    days_diff = (row['date'].date() - last['date'].date()).days
    if days_diff == 1:
        last = row
        continue

    print('=============')
    print(row['date'])
    print(last['date'])

    print((row['date'].date() - last['date'].date()).days)
    print('-------')

    missing_start_date = last['date']
    for i in range(1, days_diff):
        missing_start_date = (missing_start_date + dt.timedelta(days=1))
        print(missing_start_date)
        missing_dates = missing_dates.append({
            'date': missing_start_date,
            'coin': row['coin'],
            'value': 0.0,
            'actual_value': 0.0,
            'running_balance': 0.0,
            'status': 'Missing',
            'wallet_hash': 'n/a'}, ignore_index=True)

    print('-------========')
    last = row

result = pd.concat([df, missing_dates])
result = result.sort_values(by=['date']).reset_index(drop=True)

# print(payouts)
missing_dates.to_csv("missing_dates.csv")
## save df
# with open("source.csv", "wb") as f:
df.to_csv("source.csv")

result.to_csv("result.csv")
#
# with open("payouts.csv", "wb") as f:
# payouts.to_csv("payouts.csv")
