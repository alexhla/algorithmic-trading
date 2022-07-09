import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen



symbol = 'RCON'
print (f'\nGetting data for {symbol}...\n')

# Set up scraper
# url = f'http://finviz.com/quote.ashx?t={symbol}'
# req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
# webpage = urlopen(req).read()
# soup = soup(webpage, "html.parser")


# Read from file
url = f'finviz-rcon.html'
page = open(url)
soup = soup(page.read(), "html.parser")

data = {'priceData':None,
		'Index':None,
		'Market Cap':None,
		'Income':None,
		'Sales':None,
		'Book/sh':None,
		'Cash/sh':None,
		'Shs Outstand':None,
		'Shs Float':None,
		'Dividend':None,
		'Dividend %':None,
		'Employees':None,
		'Optionable':None,
		'Shortable':None,
		'Recom':None,
		'P/E':None,
		'Forward P/E':None,
		'PEG':None,
		'P/S':None,
		'P/B':None,
		'P/C':None,
		'P/FCF':None,
		'Quick Ratio':None,
		'Current Ratio':None,
		'Debt/Eq':None,
		'LT Debt/Eq':None,
		'SMA20':None,
		}


# Parse HTML
for row in soup.get_text().splitlines():
	if data['priceData'] == None and 'var data = {"ticker":' in row:

		left_braces = []
		right_braces = []

		for index, char in enumerate(row):
			if char == '{':
				left_braces.append(index)
			if char == '}':
				right_braces.append(index)

		data['priceData'] = json.loads(row[min(left_braces)-1:max(right_braces)+1])
		# print(f'{data} \n\ndata above is type {type(data)}')

	for key in data:
		if data[key] == None and key in row:
			data[key] = row.split(key)[1]


# Print to Terminal
for key in data:
	if key == 'priceData':
		print(f"{'Ticker:':<15}{data['priceData']['ticker']}")
		print(f"{'Last Open:':<15}{round(data['priceData']['lastOpen'], 2):.2f}")
		print(f"{'Last Close:':<15}{round(data['priceData']['lastClose'],2):.2f}")
	else:
		print(f'{key:<15}{data[key]}')