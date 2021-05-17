from argparse import ArgumentParser
from pandas import DataFrame
from time import sleep
from sys import stdout

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
ap.add_argument('-ss', '--sizzle_scanner', action='store_true')

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

	tickers = watchlists.tickers['May2020_HighBetaMicroCap'] + watchlists.tickers['stocktwits']
	query_size = 100
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

	# Get Current Volume
	temp = []
	for q in query_list:
		fundementals = r.stocks.get_fundamentals(q)
		print(fundementals)
		for f in fundementals:
			temp.append({key: f[key] for key in f.keys() & {'symbol', 'average_volume'}})

	# Convert to Data Frame
	df = DataFrame.from_dict(temp)
	df['average_volume'] = df['average_volume'].astype(float)

	df_filtered = df[df["average_volume"] < 50000]
	print(df_filtered['symbol'].tolist())



'''

Scanner

'''

if args['sizzle_scanner']:

	tickers = watchlists.tickers['May2020_HighBetaMicroCap'] + watchlists.tickers['stocktwits']
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
		rvol['30s'] = []
		rvol['60s'] = []
		rvol['90s'] = []
		rvol['2m'] = []
		rvol['3m'] = []
		rvol['4m'] = []
		rvol['5m'] = []
		rvol['7m'] = []
		rvol['9m'] = []
		rvol['11m'] = []
		rvol['13m'] = []

		latest_price = []
		price['current'] = []
		price['30s'] = []
		price['60s'] = []
		price['90s'] = []
		price['2m'] = []
		price['3m'] = []
		price['4m'] = []
		price['5m'] = []
		price['7m'] = []
		price['9m'] = []
		price['11m'] = []
		price['13m'] = []

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
				rvol['30s'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-2][i]))
			if len(rvol['history']) >= 3:
				trend = '+' if price['history'][-1][i] > price['history'][-3][i] else '-'
				rvol['60s'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-3][i]))
			if len(rvol['history']) >= 4:
				trend = '+' if price['history'][-1][i] > price['history'][-4][i] else '-'
				rvol['90s'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-4][i]))
			if len(rvol['history']) >= 5:
				trend = '+' if price['history'][-1][i] > price['history'][-5][i] else '-'
				rvol['2m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-5][i]))
			if len(rvol['history']) >= 7:
				trend = '+' if price['history'][-1][i] > price['history'][-7][i] else '-'
				rvol['3m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-7][i]))
			if len(rvol['history']) >= 9:
				trend = '+' if price['history'][-1][i] > price['history'][-9][i] else '-'
				rvol['4m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-9][i]))
			if len(rvol['history']) >= 11:
				trend = '+' if price['history'][-1][i] > price['history'][-11][i] else '-'
				rvol['5m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-11][i]))
			if len(rvol['history']) >= 15:
				trend = '+' if price['history'][-1][i] > price['history'][-15][i] else '-'
				rvol['7m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-15][i]))
			if len(rvol['history']) >= 19:
				trend = '+' if price['history'][-1][i] > price['history'][-19][i] else '-'
				rvol['9m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-19][i]))
			if len(rvol['history']) >= 23:
				trend = '+' if price['history'][-1][i] > price['history'][-23][i] else '-'
				rvol['11m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-23][i]))
			if len(rvol['history']) >= 27:
				trend = '+' if price['history'][-1][i] > price['history'][-27][i] else '-'
				rvol['13m'].append((tickers[i], trend, rvol['history'][-1][i] - rvol['history'][-27][i]))

		# Sort
		rvol['current'].sort(key=lambda x:x[1])
		rvol['30s'].sort(key=lambda x:x[1])
		rvol['60s'].sort(key=lambda x:x[1])
		rvol['90s'].sort(key=lambda x:x[1])
		rvol['2m'].sort(key=lambda x:x[1])
		rvol['3m'].sort(key=lambda x:x[1])
		rvol['4m'].sort(key=lambda x:x[1])
		rvol['5m'].sort(key=lambda x:x[1])
		rvol['7m'].sort(key=lambda x:x[1])
		rvol['9m'].sort(key=lambda x:x[1])
		rvol['11m'].sort(key=lambda x:x[1])
		rvol['13m'].sort(key=lambda x:x[1])

		# Display Results
		if len(rvol['history']) >= 27:  # 13m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}{rvol["3m"][i][0]:<4}{rvol["3m"][i][1]}{rvol["3m"][i][2]:<7}{rvol["4m"][i][0]:<4}{rvol["4m"][i][1]}{rvol["4m"][i][2]:<7}{rvol["5m"][i][0]:<4}{rvol["5m"][i][1]}{rvol["5m"][i][2]:<7}{rvol["7m"][i][0]:<4}{rvol["7m"][i][1]}{rvol["7m"][i][2]:<7}{rvol["9m"][i][0]:<4}{rvol["9m"][i][1]}{rvol["9m"][i][2]:<7}{rvol["11m"][i][0]:<4}{rvol["11m"][i][1]}{rvol["11m"][i][2]:<7}{rvol["13m"][i][0]:<4}{rvol["13m"][i][1]}{rvol["13m"][i][2]:<7}')
		elif len(rvol['history']) >= 23 and len(rvol['history']) <= 26:  # 11m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}{rvol["3m"][i][0]:<4}{rvol["3m"][i][1]}{rvol["3m"][i][2]:<7}{rvol["4m"][i][0]:<4}{rvol["4m"][i][1]}{rvol["4m"][i][2]:<7}{rvol["5m"][i][0]:<4}{rvol["5m"][i][1]}{rvol["5m"][i][2]:<7}{rvol["7m"][i][0]:<4}{rvol["7m"][i][1]}{rvol["7m"][i][2]:<7}{rvol["9m"][i][0]:<4}{rvol["9m"][i][1]}{rvol["9m"][i][2]:<7}{rvol["11m"][i][0]:<4}{rvol["11m"][i][1]}{rvol["11m"][i][2]:<7}')
		elif len(rvol['history']) >= 19 and len(rvol['history']) <= 22:  # 9m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}{rvol["3m"][i][0]:<4}{rvol["3m"][i][1]}{rvol["3m"][i][2]:<7}{rvol["4m"][i][0]:<4}{rvol["4m"][i][1]}{rvol["4m"][i][2]:<7}{rvol["5m"][i][0]:<4}{rvol["5m"][i][1]}{rvol["5m"][i][2]:<7}{rvol["7m"][i][0]:<4}{rvol["7m"][i][1]}{rvol["7m"][i][2]:<7}{rvol["9m"][i][0]:<4}{rvol["9m"][i][1]}{rvol["9m"][i][2]:<7}')
		elif len(rvol['history']) >= 15 and len(rvol['history']) <= 18:  # 7m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}{rvol["3m"][i][0]:<4}{rvol["3m"][i][1]}{rvol["3m"][i][2]:<7}{rvol["4m"][i][0]:<4}{rvol["4m"][i][1]}{rvol["4m"][i][2]:<7}{rvol["5m"][i][0]:<4}{rvol["5m"][i][1]}{rvol["5m"][i][2]:<7}{rvol["7m"][i][0]:<4}{rvol["7m"][i][1]}{rvol["7m"][i][2]:<7}')
		elif len(rvol['history']) >= 11 and len(rvol['history']) <= 14:  # 5m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}{rvol["3m"][i][0]:<4}{rvol["3m"][i][1]}{rvol["3m"][i][2]:<7}{rvol["4m"][i][0]:<4}{rvol["4m"][i][1]}{rvol["4m"][i][2]:<7}{rvol["5m"][i][0]:<4}{rvol["5m"][i][1]}{rvol["5m"][i][2]:<7}')
		elif len(rvol['history']) == 9 or len(rvol['history']) == 10:  # 4m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}{rvol["3m"][i][0]:<4}{rvol["3m"][i][1]}{rvol["3m"][i][2]:<7}{rvol["4m"][i][0]:<4}{rvol["4m"][i][1]}{rvol["4m"][i][2]:<7}')
		elif len(rvol['history']) == 7 or len(rvol['history']) == 8:  # 3m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}{rvol["3m"][i][0]:<4}{rvol["3m"][i][1]}{rvol["3m"][i][2]:<7}')
		elif len(rvol['history']) == 5 or len(rvol['history']) == 6:  # 2m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}{rvol["2m"][i][0]:<4}{rvol["2m"][i][1]}{rvol["2m"][i][2]:<7}')
		elif len(rvol['history']) == 4:  # 90s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}{rvol["90s"][i][0]:<4}{rvol["90s"][i][1]}{rvol["90s"][i][2]:<7}')
		elif len(rvol['history']) == 3:  # 60s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}{rvol["60s"][i][0]:<4}{rvol["60s"][i][1]}{rvol["60s"][i][2]:<7}')
		elif len(rvol['history']) == 2:  # 30s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<4}{rvol["30s"][i][1]}{rvol["30s"][i][2]:<7}')
		else: # elif len(rvol['history']) == 1:
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<6}')

		print('RVOL{:<8}30s Δ{:<7}60s Δ{:<7}90s Δ{:<7}2m Δ{:<8}3m Δ{:<8}4m Δ{:<8}5m Δ{:<8}7m Δ{:<8}9m Δ{:<8}11m Δ{:<7}13m Δ{:<7}'.format('','','','','','','','','','','',''))


		# Debug 
		# print(f'ʕಠಿᴥಠʔ Tickers are {tickers} --- Type: {type(tickers)} --- Length: {len(tickers)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {volume} --- Type: {type(volume)} --- Length: {len(volume)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {rvol["history"]} --- Type: {type(rvol["history"])} --- Length: {len(rvol["history"])} --- Element Length: {len(rvol["history"][0])}\n')
		# print(f'ʕಠಿᴥಠʔ Price is {price["history"]} --- Type: {type(price["history"])} --- Length: {len(price["history"])} --- Element Length: {len(price["history"][0])}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {rvol["30s"]} --- Type: {type(rvol["30s"])} --- Length: {len(rvol["30s"])}\n')

		# Wait
		wait_seconds = 30
		elapsed_minutes = ((len(rvol['history'])-1) * wait_seconds) / 60 
		for i in range(0, wait_seconds+1):
			stdout.write('\r')
			stdout.write(f'{elapsed_minutes} Minutes Elapsed. Updating in {wait_seconds-i} Seconds...')
			stdout.flush()
			sleep(1)
		print('\n\nWorking...\n')