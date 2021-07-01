from argparse import ArgumentParser
from pandas import DataFrame
from time import sleep
from sys import stdout
import csv

# import robin_stocks as r  # package name differs with version
import robin_stocks.robinhood as r

# local imports
import config
from stocklists import blacklist

# Login to Robinhood
r.login(config.ROBINHOOD_EMAIL, config.ROBINHOOD_PASSWORD)

# Instantiate the argument parser object
ap = ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-i', '--info', nargs='+', metavar=['TICKERS'])
ap.add_argument('-vc', '--volume_checker', action='store_true')
ap.add_argument('-vh', '--volume_history', action='store_true')
ap.add_argument('-ss', '--sizzle_scanner', action='store_true')


ap.add_argument('-goc', '--get_options_chains', nargs='+', metavar=['TICKERS'])


# Parse user arguments
args = vars(ap.parse_args())
print(f'args --- {args}\n')


test_tickers = ['SPY','TSLA','UUU','RMED','CLVS','CLOV']


'''

Info

'''

if args['get_options_chains']:

	tickers = args['get_options_chains']
	data = []


	print(f'Requesting...')


	# print('Requesting Options by Expiration...')
	# options_by_expiration = r.options.find_options_by_expiration(tickers, '2021-06-18')
	# for index, element in enumerate(options_by_expiration):
	# 	print(f'ʕಠಿᴥಠʔ  {index} | {element}\n')

	# print('Requesting Options by Expiration and Strike...')
	# find_options_by_expiration_and_strike = r.options.find_options_by_expiration_and_strike(tickers, '2021-06-18', '7.0000')
	# for index, element in enumerate(find_options_by_expiration_and_strike):
	# 	print(f'ʕಠಿᴥಠʔ  {index} | {element}\n')


	#### NOT WORKING
	# print('Requesting Options by find_options_by_specific_profitability...')
	# find_options_by_specific_profitability = r.options.find_options_by_specific_profitability(tickers, profitFloor=0.0, profitCeiling=0.1)
	# for index, element in enumerate(find_options_by_specific_profitability):
	# 	print(f'ʕಠಿᴥಠʔ  {index} | {element}\n')


	# print('Requesting Options by Strike...')
	# find_options_by_strike = r.options.find_options_by_strike(tickers, '6.0000')
	# for index, element in enumerate(find_options_by_strike):
	# 	print(f'ʕಠಿᴥಠʔ  {index} | {element}\n')

	# print('Requesting Tradable Options...')
	# find_tradable_options = r.options.find_tradable_options(tickers[0])
	# for index, element in enumerate(find_tradable_options):
	# 	print(f'ʕಠಿᴥಠʔ  {index} | {element}\n')

	# print('Requesting Options Chains...')
	# get_chains = r.options.get_chains(tickers[0])
	# print(f'ʕಠಿᴥಠʔ  {get_chains}')

	print('Requesting Option Historicals...')
	get_option_historicals = r.options.get_option_historicals(tickers[0], expirationDate='2021-06-18', strikePrice='6.0000', optionType='call')
	for index, element in enumerate(get_option_historicals):
		print(f'ʕಠಿᴥಠʔ  {index} | {element}\n')


	# get_option_historicals
	# get_option_instrument_data
	# get_option_market_data



	# # Merge Info into Single Dictionary
	# for i, d in enumerate(data):
	# 	d['ticker'] = tickers[i]
	# 	d['latest_price'] = latest_price[i]

	# # Compute RVOL
	# df = DataFrame.from_dict(data)
	# df['RVOL'] = df['volume'].astype(float) / df['average_volume'].astype(float)

	# # Display Results
	# for index, row in df.iterrows():
	# 	print(f'{row}\n')



'''

Info

'''

if args['info']:

	tickers = args['info']
	data = []

	# Get Fundamentals
	fundementals = r.stocks.get_fundamentals(tickers)
	print(f'ʕಠಿᴥಠʔ Fundamentals {fundementals}')
	for f in fundementals:
		data.append({key: f[key] for key in f.keys() & {'market_cap', 'shares', 'float', 'volume', 'average_volume', 'open'}})

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

	tickers = test_tickers
	query_size = 100
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

	# Get Current Volume
	temp = []
	for q in query_list:
		fundementals = r.stocks.get_fundamentals(q)
		# print(fundementals)
		for f in fundementals:
			temp.append({key: f[key] for key in f.keys() & {'symbol', 'average_volume'}})

	# Convert to Data Frame
	df = DataFrame.from_dict(temp)
	df['average_volume'] = df['average_volume'].astype(float)
	print(df)

	# df_filtered = df[df["average_volume"] < 50000]
	# print(df_filtered['symbol'].tolist())



'''
Get Volume History Maximum
'''

if args['volume_history']:
	tickers = test_tickers
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

	print(df_hour_month)

	# Get Max Volume for Each Timeframe
	for t in tickers:
		max_5min_week = df_5min_week[df_5min_week["symbol"] == t].max().to_dict()['volume']
		max_hour_month = df_hour_month[df_hour_month["symbol"] == t].max().to_dict()['volume']
		volume_history[t] = [max_5min_week, max_hour_month]

	print(volume_history)



'''

Scanner

'''

if args['sizzle_scanner']:

	tickers = []
	with open('stocktwits_watchlist.tsv', 'r') as in_file:
		tsv_reader = csv.reader(in_file, delimiter='\t')
		for row in tsv_reader:
			print(row)
			if row[0] not in blacklist:
				if '.CA' not in row[0]:
					tickers.append(row[0])

	rvol = {}
	price = {}
	rvol['history'] = []
	price['history'] = []
	query_size = 100  # 100 max per API Request
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])
		print(f'ʕಠಿᴥಠʔ Query List Length is {len(query_list)}')

	while True:

		volume = []
		rvol['current'] = []
		rvol['15s'] = []
		rvol['30s'] = []
		rvol['45s'] = []
		rvol['60s'] = []
		rvol['75s'] = []
		rvol['90s'] = []
		rvol['105s'] = []
		rvol['120s'] = []
		rvol['135s'] = []
		rvol['150s'] = []
		rvol['165s'] = []
		rvol['180s'] = []


		latest_price = []
		price['current'] = []
		price['15s'] = []
		price['30s'] = []
		price['45s'] = []
		price['60s'] = []
		price['75s'] = []
		price['90s'] = []
		price['105s'] = []
		price['120s'] = []
		price['135s'] = []
		price['150s'] = []
		price['165s'] = []
		price['180s'] = []

		# Get Current Volume and Price
		for i, q in enumerate(query_list):
			# print(f'ʕಠಿᴥಠʔ Requesting Query {i}/{len(query_list)}')
			fundementals = r.stocks.get_fundamentals(q)
			temp_price = r.stocks.get_latest_price(q, priceType=None, includeExtendedHours=True)
			for f in fundementals:
				volume.append({key: f[key] for key in f.keys() & {'volume', 'average_volume'}})
			for p in temp_price:
				latest_price.append(round(float(p), 2))
		price['history'].append(latest_price)

		# Convert to Data Frame and Compute RVOL
		df = DataFrame.from_dict(volume)
		df['RVOL'] = (df['volume'].astype(float) / df['average_volume'].astype(float)).round(2)
		rvol['history'].append(df['RVOL'].tolist())

		# Create (Ticker, RVOL) Pairs for Sorting Current RVOL
		for i in range(len(tickers)):
			rvol['current'].append((tickers[i], rvol['history'][-1][i]))

		# Calculate Price Trend and RVOL Delta for Each Timeframe
		for i in range(len(tickers)):
			if len(rvol['history']) >= 2:
				trend = '+' if price['history'][-1][i] > price['history'][-2][i] else '-'
				rvol['15s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-2][i], 2)))
			if len(rvol['history']) >= 3:
				trend = '+' if price['history'][-1][i] > price['history'][-3][i] else '-'
				rvol['30s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-3][i], 2)))
			if len(rvol['history']) >= 4:
				trend = '+' if price['history'][-1][i] > price['history'][-4][i] else '-'
				rvol['45s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-4][i], 2)))
			if len(rvol['history']) >= 5:
				trend = '+' if price['history'][-1][i] > price['history'][-5][i] else '-'
				rvol['60s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-5][i], 2)))
			if len(rvol['history']) >= 6:
				trend = '+' if price['history'][-1][i] > price['history'][-6][i] else '-'
				rvol['75s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-6][i], 2)))
			if len(rvol['history']) >= 7:
				trend = '+' if price['history'][-1][i] > price['history'][-7][i] else '-'
				rvol['90s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-7][i], 2)))
			if len(rvol['history']) >= 8:
				trend = '+' if price['history'][-1][i] > price['history'][-8][i] else '-'
				rvol['105s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-8][i], 2)))
			if len(rvol['history']) >= 9:
				trend = '+' if price['history'][-1][i] > price['history'][-9][i] else '-'
				rvol['120s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-9][i], 2)))
			if len(rvol['history']) >= 10:
				trend = '+' if price['history'][-1][i] > price['history'][-10][i] else '-'
				rvol['135s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-10][i], 2)))
			if len(rvol['history']) >= 11:
				trend = '+' if price['history'][-1][i] > price['history'][-11][i] else '-'
				rvol['150s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-11][i], 2)))
			if len(rvol['history']) >= 12:
				trend = '+' if price['history'][-1][i] > price['history'][-12][i] else '-'
				rvol['165s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-12][i], 2)))
			if len(rvol['history']) >= 13:
				trend = '+' if price['history'][-1][i] > price['history'][-13][i] else '-'
				rvol['180s'].append((tickers[i], trend, round(rvol['history'][-1][i] - rvol['history'][-13][i], 2)))

		# Sort
		rvol['current'].sort(key=lambda x:x[1])
		rvol['15s'].sort(key=lambda x:x[2])
		rvol['30s'].sort(key=lambda x:x[2])
		rvol['45s'].sort(key=lambda x:x[2])
		rvol['60s'].sort(key=lambda x:x[2])
		rvol['75s'].sort(key=lambda x:x[2])
		rvol['90s'].sort(key=lambda x:x[2])
		rvol['105s'].sort(key=lambda x:x[2])
		rvol['120s'].sort(key=lambda x:x[2])
		rvol['135s'].sort(key=lambda x:x[2])
		rvol['150s'].sort(key=lambda x:x[2])
		rvol['165s'].sort(key=lambda x:x[2])
		rvol['180s'].sort(key=lambda x:x[2])

		# Display Results
		if len(rvol['history']) >= 13:  # 180s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["105s"][i][0]:<4}{rvol["105s"][i][1]}{rvol["105s"][i][2]:<7}{rvol["120s"][i][0]:<4}{rvol["120s"][i][1]}{rvol["120s"][i][2]:<7}{rvol["135s"][i][0]:<4}{rvol["135s"][i][1]}{rvol["135s"][i][2]:<7}{rvol["150s"][i][0]:<4}{rvol["150s"][i][1]}{rvol["150s"][i][2]:<7}{rvol["165s"][i][0]:<4}{rvol["165s"][i][1]}{rvol["165s"][i][2]:<7}{rvol["180s"][i][0]:<4}{rvol["180s"][i][1]}{rvol["180s"][i][2]:<7}')
		elif len(rvol['history']) == 12:  # 165s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["105s"][i][0]:<4}{rvol["105s"][i][1]}{rvol["105s"][i][2]:<7}{rvol["120s"][i][0]:<4}{rvol["120s"][i][1]}{rvol["120s"][i][2]:<7}{rvol["135s"][i][0]:<4}{rvol["135s"][i][1]}{rvol["135s"][i][2]:<7}{rvol["150s"][i][0]:<4}{rvol["150s"][i][1]}{rvol["150s"][i][2]:<7}{rvol["165s"][i][0]:<4}{rvol["165s"][i][1]}{rvol["165s"][i][2]:<7}')
		elif len(rvol['history']) == 11:  # 150s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["105s"][i][0]:<4}{rvol["105s"][i][1]}{rvol["105s"][i][2]:<7}{rvol["120s"][i][0]:<4}{rvol["120s"][i][1]}{rvol["120s"][i][2]:<7}{rvol["135s"][i][0]:<4}{rvol["135s"][i][1]}{rvol["135s"][i][2]:<7}{rvol["150s"][i][0]:<4}{rvol["150s"][i][1]}{rvol["150s"][i][2]:<7}')
		elif len(rvol['history']) == 10:  # 135s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["105s"][i][0]:<4}{rvol["105s"][i][1]}{rvol["105s"][i][2]:<7}{rvol["120s"][i][0]:<4}{rvol["120s"][i][1]}{rvol["120s"][i][2]:<7}{rvol["135s"][i][0]:<4}{rvol["135s"][i][1]}{rvol["135s"][i][2]:<7}')
		elif len(rvol['history']) == 9:  # 120s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["105s"][i][0]:<4}{rvol["105s"][i][1]}{rvol["105s"][i][2]:<7}{rvol["120s"][i][0]:<4}{rvol["120s"][i][1]}{rvol["120s"][i][2]:<7}')
		elif len(rvol['history']) == 8:  # 105s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["105s"][i][0]:<4}{rvol["105s"][i][1]}{rvol["105s"][i][2]:<7}')
		elif len(rvol['history']) == 7:  # 90s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}')
		elif len(rvol['history']) == 6:  # 75s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["75s"][i][0]:<4}{rvol["75s"][i][1]}{rvol["75s"][i][2]:<7}')
		elif len(rvol['history']) == 5:  # 60s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}')
		elif len(rvol['history']) == 4:  # 45s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["45s"][i][0]:<4}{rvol["45s"][i][1]}{rvol["45s"][i][2]:<7}')
		elif len(rvol['history']) == 3:  # 30s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}')
		elif len(rvol['history']) == 2:  # 15s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["15s"][i][0]:<4}{rvol["15s"][i][1]}{rvol["15s"][i][2]:<7}')
		else: # elif len(rvol['history']) == 1:
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<6}')

		print('RVOL{:<8}15s Δ{:<7}30s Δ{:<7}45s Δ{:<7}60s Δ{:<7}75s Δ{:<7}90s Δ{:<7}105s Δ{:<6}120s Δ{:<6}135s Δ{:<6}150s Δ{:<6}165s Δ{:<6}180s Δ{:<6}'.format('','','','','','','','','','','','',''))
		print('{:<48}1m{:<46}2m{:<46}3m'.format('','',''))

		if len(rvol['15s']) >= 1:
			if rvol["15s"][-1][2] >= 0.1:
				print(f'{rvol["15s"][-1][0]} {rvol["15s"][-1][2]} --- Alert --- (⊙.⊙(☉̃ₒ☉)⊙.⊙) --- Alert --- (⊙.⊙(☉̃ₒ☉)⊙.⊙)  --- Alert --- (⊙.⊙(☉̃ₒ☉)⊙.⊙)\n')


		# Debug 
		# print(f'ʕಠಿᴥಠʔ Tickers are {tickers} --- Type: {type(tickers)} --- Length: {len(tickers)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {volume} --- Type: {type(volume)} --- Length: {len(volume)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {rvol["history"]} --- Type: {type(rvol["history"])} --- Length: {len(rvol["history"])} --- Element Length: {len(rvol["history"][0])}\n')
		# print(f'ʕಠಿᴥಠʔ Price is {price["history"]} --- Type: {type(price["history"])} --- Length: {len(price["history"])} --- Element Length: {len(price["history"][0])}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {rvol["30s"]} --- Type: {type(rvol["30s"])} --- Length: {len(rvol["30s"])}\n')

		# Wait
		wait_seconds = 15
		elapsed_minutes = ((len(rvol['history'])-1) * wait_seconds) / 60 
		for i in range(0, wait_seconds+1):
			stdout.write('\r')
			stdout.write(f'{elapsed_minutes} Minutes Elapsed. Updating in {wait_seconds-i} Seconds...')
			stdout.flush()
			sleep(1)
		print('\n\nWorking...\n')