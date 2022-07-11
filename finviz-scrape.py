from csv import writer
from json import loads
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

# Declare variables
tickers = set()
priceData = {}
data = {'ticker':None,
		'lastOpen':None,
		'lastClose':None,
		'Index':None,
		'Market Cap':None,
		'Income':None,
		'Sales':None,
		'Book/sh':None,
		'Cash/sh':None,
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
		'EPS (ttm)':None,
		'EPS next Y':None,
		'EPS next Q':None,
		'EPS this Y':None,
		'EPS next Y':None,
		'EPS next 5Y':None,
		'EPS past 5Y':None,
		'Sales past 5Y':None,
		'Sales Q/Q':None,
		'EPS Q/Q':None,
		'Earnings':None,
		'SMA50':None,
		'Insider Own':None,
		'Insider Trans':None,
		'Inst Own':None,
		'ROA':None,
		'ROE':None,
		'ROI':None,
		'Gross Margin':None,
		'Oper. Margin':None,
		'Profit Margin':None,
		'Payout':None,
		'Shs Outstand':None,
		'Shs Float':None,
		'Short Float':None,
		'Short Ratio':None,
		'Target Price':None,
		'52W Range':None,
		'52W High':None,
		'52W Low':None,
		'RSI (14)':None,
		'Rel Volume':None,
		'Avg Volume':None,
		'Volume':None,
		'Perf Week':None,
		'Perf Month':None,
		'Perf Quarter':None,
		'Perf Half Y':None,
		'Perf Year':None,
		'Perf YTD':None,
		'Beta':None,
		'ATR':None,
		'Volatility':None,
		'Prev Close':None,
		'Price':None,
		'Change':None,
	}

# Get tickers
with open('tickers-nasdaq-07-2022.csv', 'r') as file:
	for index, row in enumerate(file):
		if index == 0:
			continue
		
		ticker = row.split(',')[0]
		
		if '^' in ticker or '/' in ticker:
			continue
		
		tickers.add(ticker)

# Open TSV file
with open('finviz.tsv', 'w+') as file:
	tsv_writer = writer(file, delimiter='\t')
	tsv_writer.writerow(data.keys())
	for ticker in tickers:
		print (f'\nScraping {ticker}...\n')
		url = f'http://finviz.com/quote.ashx?t={ticker}'
		req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		try:
			webpage = urlopen(req).read()
		except Exception as e:
			print(f'{ticker} --- {e}')
			continue
		soupObject = soup(webpage, "html.parser")

		# Parse Javascript
		soupScript = soupObject.find_all('script')
		for row in soupScript:
			rowText = row.text
			if 'var data' in rowText:

				left_braces = []
				right_braces = []

				for index, char in enumerate(rowText):
					if char == '{':
						left_braces.append(index)
					if char == '}':
						right_braces.append(index)

				priceData = loads(rowText[left_braces[1]:right_braces[-2]+1])
				if priceData['lastOpen'] == None or priceData['lastClose'] == None:
					print('skipping')
					continue
				data['ticker'] = priceData['ticker']
				data['lastOpen'] = round(priceData['lastOpen'], 2)
				data['lastClose'] = round(priceData['lastClose'],2)

		# Parse HTML
		soupText = soupObject.get_text().splitlines()
		for row in soupText:
			for key in data:
				if data[key] == None and key in row:
					data[key] = row.split(key)[1]

		# Write to TSV
		tsv_writer.writerow(data.values())

		# Print to Terminal
		for key in data:
			print(f'{key:<15}{data[key]}')