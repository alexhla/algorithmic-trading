from argparse import ArgumentParser
from sys import stdout
import datetime
import time
import pandas as pd

#import robin_stocks as r  # package name differs with version
import robin_stocks.robinhood as r

# local imports
import config
import stockdictionary

# Login to Robinhood
r.login(config.ROBINHOOD_EMAIL, config.ROBINHOOD_PASSWORD)

# Instantiate the argument parser object
ap = ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-i', '--info', nargs='+', metavar=['TICKERS'],
	help='')

ap.add_argument('-rvol', '--rvol_scanner', nargs=1, metavar=['INTERVAL'],
	help='')

# Parse user arguments
args = vars(ap.parse_args())
print(f'args --- {args}\n')



if args['info']:

	tickers = args['info']
	data = {'tickers':tickers}

	# Get Stock Exchange MIC Code
	instrument = r.stocks.find_instrument_data(tickers)
	data['stock_exchange'] = instrument[0]['market'].split('/')[-2]

	# Get Lastest Trade Price
	latest_price = r.stocks.get_latest_price(tickers, priceType=None, includeExtendedHours=True)
	data['latest_price'] = round(float(latest_price[0]), 2)

	# Get Market Cap, Volume, Shares, and Float
	fundementals = r.stocks.get_fundamentals(tickers)
	df = pd.DataFrame.from_dict(fundementals)
	for col in df.columns:
		if any(word in col for word in ['market_cap', 'volume', 'shares', 'float']):
			data[col] = round(float(df[col][0]), 2)

	# Compute RVOL
	data['RVOL'] = round(data['volume'] / data['average_volume'], 2)
	data['RVOL_2_weeks'] = round(data['volume'] / data['average_volume_2_weeks'], 2)

	# Get Volume History
	# historicals = r.stocks.get_stock_historicals(tickers, interval='5minute', span='week')#, bounds='extended')
	# for d in historicals:
	# 	data.setdefault('volume_history', []).append((d['begins_at'], d['volume']))

	# Print Data 
	for k,v in data.items():
		print(f'{k:<25}{v}')




if args['rvol_scanner']:

	tickers = stockdictionary.tickers['microcap_float10M_price10USD']
	interval = int(args['rvol_scanner'][0])
	data = {}
	query_size = 100
	query_list = []
	rvol = []

	# Build Query List
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])
	data = {'ticker':query_list}


	while True:
		print('\n\nProcuring RVOL...')

		# Get Volume
		for q in query_list:
			fundementals = r.stocks.get_fundamentals(q)
			df = pd.DataFrame.from_dict(fundementals)
			for col in df.columns:
				if 'volume' in col:
					data.setdefault(col, []).append(df[col].astype(float).tolist())

		# Compute RVOL
		for i in range(0, len(data['ticker'])):
			current = []
			for j in range(0, len(data['ticker'][i])):
				current.append(data['volume'][i][j] / data['average_volume'][i][j])
			data.setdefault('RVOL', []).append(current)

		# Generate List of (Ticker, RVOL) Tuple Pairs for Sorting
		rvol = []
		for i in range(0, len(data['ticker'])):
			for j in range(0, len(data['ticker'][i])):
				if data['ticker'][i][j] not in stockdictionary.tickers['blacklist']:
					rvol.append((data['ticker'][i][j], data['RVOL'][i][j]))
		rvol.sort(key=lambda x:x[1])

		# Display Results
		for x in rvol:
			print(f'{x[0]:<6}{round(x[1],3)}')
		stdout.write('\n')

		# Debug 
		# print(f'ʕಠಿᴥಠʔ Tickers are {data["ticker"]} {type(data["ticker"])}\n')
		# print(f'ʕಠಿᴥಠʔ Ticker Count is {len(data["ticker"])}\n')
		# print(f'ʕಠಿᴥಠ ʔtytRequest is {request} {type(request)}\n')
		# print(f'ʕಠಿᴥಠʔ Fundementals are {fundementals} {type(fundementals)}\n')
		# print(f'ʕಠಿᴥಠʔ Data is {data} {type(data)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {data["volume"]} {type(data["volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Volume Count is {len(data["volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Average Volume is {data["average_volume"]} {type(data["average_volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Average Volume Count is {len(data["average_volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {data["RVOL"]} {type(data["RVOL"])}\n')
		# for key in data:
		# 	print(f'ʕಠಿᴥಠʔ {key} {len(data[key])}')

		# Wait
		for i in range(0, interval):
			stdout.write('\r')
			stdout.write(f'Next Procurement in {interval-i} Seconds...')
			stdout.flush()
			time.sleep(1)

