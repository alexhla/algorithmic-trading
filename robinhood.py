from argparse import ArgumentParser
from datetime import datetime
from pandas import DataFrame
from time import sleep
from sys import stdout
from csv import writer
from subprocess import run

#import robin_stocks as r  # package name differs with version
import robin_stocks.robinhood as r

# local imports
import config
import watchlists

# Login to Robinhood
r.login(config.ROBINHOOD_EMAIL, config.ROBINHOOD_PASSWORD)

# Instantiate the argument parser object
ap = ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-i', '--info', nargs='+', metavar=['TICKERS'])
ap.add_argument('-vc', '--volume_checker', action='store_true')
ap.add_argument('-vs', '--volume_scanner', action='store_true')

# Parse user arguments
args = vars(ap.parse_args())
print(f'args --- {args}\n')



'''

Info

'''

if args['info']:

	tickers = args['info']
	data = []

	# Get Fundamentals
	fundementals = r.stocks.get_fundamentals(tickers)
	for f in fundementals:
		data.append({key: f[key] for key in f.keys() & {'market_cap', 'shares', 'float', 'volume', 'average_volume'}})

	# Get Lastest Trade Price
	latest_price = r.stocks.get_latest_price(tickers, priceType=None, includeExtendedHours=True)

	# Merge Info into Single Dictionary
	for i, d in enumerate(data):
		d['ticker'] = tickers[i]
		d['latest_price'] = latest_price[i]

	# Compute RVOL
	df = DataFrame.from_dict(data)
	df['RVOL'] = df['volume'].astype(float) / df['average_volume'].astype(float)

	# Display Results
	for index, row in df.iterrows():
		print(f'{row}\n')


'''

Volume Checker

'''

if args['volume_checker']:

	selection = 'schwab_05_2020'
	tickers = watchlists.tickers[selection]
	query_size = 100
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

	# Get Current Volume
	temp = []
	for q in query_list:
		fundementals = r.stocks.get_fundamentals(q)
		for f in fundementals:
			temp.append({key: f[key] for key in f.keys() & {'symbol', 'average_volume'}})

	# Convert to Data Frame
	df = DataFrame.from_dict(temp)
	df['average_volume'] = df['average_volume'].astype(float)

	df_filtered = df[df["average_volume"] < 50000]
	print(df_filtered['symbol'].tolist())


'''

Get Volume History Maximum

'''
def get_volume_history_maximums(selection):

	tickers = watchlists.tickers[selection]
	volume_history = {}
	query_size = 75
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

	# Get Volume History
	historicals_5min_week = []
	historicals_hour_month = []
	for i, q in enumerate(query_list):
		print(f'Requesting Volume History Query List {i+1} of {len(query_list)}')
		
		history = r.stocks.get_stock_historicals(q, interval='5minute', span='week')
		for h in history:
			historicals_5min_week.append({key: h[key] for key in h.keys() & {'begins_at', 'symbol', 'volume', 'session'}})
			
		history = r.stocks.get_stock_historicals(q, interval='hour', span='month')
		for h in history:
			historicals_hour_month.append({key: h[key] for key in h.keys() & {'begins_at', 'symbol', 'volume', 'session'}})
		
	df_5min_week = DataFrame.from_dict(historicals_5min_week)	
	df_hour_month = DataFrame.from_dict(historicals_hour_month)

	# Get Max Volume for Each Timeframe
	for t in tickers:
		max_5min_week = df_5min_week[df_5min_week["symbol"] == t].max().to_dict()['volume']
		max_hour_month = df_hour_month[df_hour_month["symbol"] == t].max().to_dict()['volume']
		volume_history[t] = [max_5min_week, max_hour_month]

	return volume_history


'''

Scanner

'''

if args['volume_scanner']:

	tickers = watchlists.tickers['foobar']
	rvol = {}
	rvol['history'] = []
	query_size = 100  # 100 max per API Request
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

	while True:
		rvol['current'] = []
		rvol['30s'] = []
		rvol['60s'] = []
		rvol['90s'] = []
		rvol['2m'] = []
		rvol['3m'] = []
		rvol['4m'] = []
		rvol['5m'] = []
		rvol['10m'] = []
		rvol['15m'] = []

		# Get Current Volume
		temp_volume = []
		for q in query_list:
			fundementals = r.stocks.get_fundamentals(q)
			for f in fundementals:
				temp_volume.append({key: f[key] for key in f.keys() & {'volume', 'average_volume'}})

		# Convert to Data Frame and Compute RVOL
		df = DataFrame.from_dict(temp_volume)
		df['RVOL'] = (df['volume'].astype(float) / df['average_volume'].astype(float)).round(3)
		rvol['history'].append(df['RVOL'].tolist())

		# Create (Ticker, RVOL) Pairs for Sorting Current RVOL
		for i in range(len(tickers)):
			rvol['current'].append((tickers[i], rvol['history'][-1][i]))

		# Calculate RVOL Delta for Each Timeframe
		for i in range(len(tickers)):
			if len(rvol['history']) >= 2:
				rvol['30s'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-2][i]))
			if len(rvol['history']) >= 3:
				rvol['60s'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-3][i]))
			if len(rvol['history']) >= 4:
				rvol['90s'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-4][i]))
			if len(rvol['history']) >= 5:
				rvol['2m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-5][i]))
			if len(rvol['history']) >= 7:
				rvol['3m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-7][i]))
			if len(rvol['history']) >= 9:
				rvol['4m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-9][i]))
			if len(rvol['history']) >= 11:
				rvol['5m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-11][i]))
			if len(rvol['history']) >= 21:
				rvol['10m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-21][i]))
			if len(rvol['history']) >= 31:
				rvol['15m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-31][i]))

		# Sort
		rvol['current'].sort(key=lambda x:x[1])
		rvol['30s'].sort(key=lambda x:x[1])
		rvol['60s'].sort(key=lambda x:x[1])
		rvol['90s'].sort(key=lambda x:x[1])
		rvol['2m'].sort(key=lambda x:x[1])
		rvol['4m'].sort(key=lambda x:x[1])
		rvol['3m'].sort(key=lambda x:x[1])
		rvol['5m'].sort(key=lambda x:x[1])
		rvol['10m'].sort(key=lambda x:x[1])
		rvol['15m'].sort(key=lambda x:x[1])

		if len(rvol['history']) == 2:
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<6}{rvol["current"][i][1]:<10}{rvol["30s"][i][0]:<6}{rvol["30s"][i][1]:<10}')
			print('RVOL{:<12}30s Δ'.format(' '))
		# elif len(rvol) == 3:
		# 	for i in range(0, len(tickers)):
		# 		print(f'{rvol_total[i][0]:<6}{rvol_total[i][1]:<10}{rvol_30s[i][0]:<6}{rvol_30s[i][1]:<10}{rvol_60s[i][0]:<6}{rvol_60s[i][1]:<10}')
		# 	print('RVOL{:<12}30s{:<6}60s'.format(' ', ' '))

			# for i in range(0, len(tickers)):
			# 	print(f'{rvol_total[i][0]:<6}{rvol_total[i][1]:<10}{rvol_30s[i][0]:<6}{rvol_30s[i][1]:<10}{rvol_60s[i][0]:<6}{rvol_60s[i][1]:<10}{rvol_90s[i][0]:<6}{rvol_90s[i][1]:<12}')
			# print('RVOL{:<12}30s{:<6}60s{:<8}90s'.format(' ', ' ', ' '))

		# Debug 
		# print(f'ʕಠಿᴥಠʔ Tickers are {tickers} --- Type: {type(tickers)} --- Length: {len(tickers)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {volume} --- Type: {type(volume)} --- Length: {len(volume)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {rvol} --- Type: {type(rvol)} --- Length: {len(rvol)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL Current is {rvol_total} --- Type: {type(rvol_total)} --- Length: {len(rvol_total)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL 30s is {rvol_30s} --- Type: {type(rvol_30s)} --- Length: {len(rvol_30s)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL 60s is {rvol_60s} --- Type: {type(rvol_60s)} --- Length: {len(rvol_60s)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL 90s is {rvol_90s} --- Type: {type(rvol_90s)} --- Length: {len(rvol_90s)}\n')

		# Wait
		wait_seconds = 5
		for i in range(0, wait_seconds+1):
			stdout.write('\r')
			stdout.write(f'Updating in {wait_seconds-i} Seconds...')
			stdout.flush()
			sleep(1)
		print('\n\nWorking...\n')