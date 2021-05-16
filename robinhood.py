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

Scanner

'''

if args['sizzle_scanner']:

	tickers = watchlists.tickers['schwab_05_2020']
	rvol = {}
	rvol['history'] = []
	query_size = 100  # 100 max per API Request
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

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

		# Get Current Volume
		for q in query_list:
			fundementals = r.stocks.get_fundamentals(q)
			for f in fundementals:
				volume.append({key: f[key] for key in f.keys() & {'volume', 'average_volume'}})

		# Convert to Data Frame and Compute RVOL
		df = DataFrame.from_dict(volume)
		df['RVOL'] = (df['volume'].astype(float) / df['average_volume'].astype(float)).round(2)
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
			if len(rvol['history']) >= 15:
				rvol['7m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-15][i]))
			if len(rvol['history']) >= 19:
				rvol['9m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-19][i]))
			if len(rvol['history']) >= 23:
				rvol['11m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-23][i]))
			if len(rvol['history']) >= 27:
				rvol['13m'].append((tickers[i], rvol['history'][-1][i] - rvol['history'][-27][i]))

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
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}{rvol["3m"][i][0]:<5}{rvol["3m"][i][1]:<7}{rvol["4m"][i][0]:<5}{rvol["4m"][i][1]:<7}{rvol["5m"][i][0]:<5}{rvol["5m"][i][1]:<7}{rvol["7m"][i][0]:<5}{rvol["7m"][i][1]:<7}{rvol["9m"][i][0]:<5}{rvol["9m"][i][1]:<7}{rvol["11m"][i][0]:<5}{rvol["11m"][i][1]:<7}{rvol["13m"][i][0]:<5}{rvol["13m"][i][1]:<7}')
		elif len(rvol['history']) >= 23 and len(rvol['history']) <= 26:  # 11m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}{rvol["3m"][i][0]:<5}{rvol["3m"][i][1]:<7}{rvol["4m"][i][0]:<5}{rvol["4m"][i][1]:<7}{rvol["5m"][i][0]:<5}{rvol["5m"][i][1]:<7}{rvol["7m"][i][0]:<5}{rvol["7m"][i][1]:<7}{rvol["9m"][i][0]:<5}{rvol["9m"][i][1]:<7}{rvol["11m"][i][0]:<5}{rvol["11m"][i][1]:<7}')
		elif len(rvol['history']) >= 19 and len(rvol['history']) <= 22:  # 9m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}{rvol["3m"][i][0]:<5}{rvol["3m"][i][1]:<7}{rvol["4m"][i][0]:<5}{rvol["4m"][i][1]:<7}{rvol["5m"][i][0]:<5}{rvol["5m"][i][1]:<7}{rvol["7m"][i][0]:<5}{rvol["7m"][i][1]:<7}{rvol["9m"][i][0]:<5}{rvol["9m"][i][1]:<7}')
		elif len(rvol['history']) >= 15 and len(rvol['history']) <= 18:  # 7m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}{rvol["3m"][i][0]:<5}{rvol["3m"][i][1]:<7}{rvol["4m"][i][0]:<5}{rvol["4m"][i][1]:<7}{rvol["5m"][i][0]:<5}{rvol["5m"][i][1]:<7}{rvol["7m"][i][0]:<5}{rvol["7m"][i][1]:<7}')
		elif len(rvol['history']) >= 11 and len(rvol['history']) <= 14:  # 5m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}{rvol["3m"][i][0]:<5}{rvol["3m"][i][1]:<7}{rvol["4m"][i][0]:<5}{rvol["4m"][i][1]:<7}{rvol["5m"][i][0]:<5}{rvol["5m"][i][1]:<7}')
		elif len(rvol['history']) == 9 or len(rvol['history']) == 10:  # 4m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}{rvol["3m"][i][0]:<5}{rvol["3m"][i][1]:<7}{rvol["4m"][i][0]:<5}{rvol["4m"][i][1]:<7}')
		elif len(rvol['history']) == 7 or len(rvol['history']) == 8:  # 3m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}{rvol["3m"][i][0]:<5}{rvol["3m"][i][1]:<7}')
		elif len(rvol['history']) == 5 or len(rvol['history']) == 6:  # 2m
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}{rvol["2m"][i][0]:<5}{rvol["2m"][i][1]:<7}')
		elif len(rvol['history']) == 4:  # 90s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}{rvol["90s"][i][0]:<5}{rvol["90s"][i][1]:<7}')
		elif len(rvol['history']) == 3:  # 60s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]:<7}{rvol["60s"][i][0]:<5}{rvol["60s"][i][1]:<7}')
		elif len(rvol['history']) == 2:  # 30s
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<7}{rvol["30s"][i][0]:<5}{rvol["30s"][i][1]}')
		else: # elif len(rvol['history']) == 1:
			for i in range(len(tickers)):
				print(f'{rvol["current"][i][0]:<5}{rvol["current"][i][1]:<6}')

		print('RVOL{:<8}30s Δ{:<7}60s Δ{:<7}90s Δ{:<7}2m Δ{:<8}3m Δ{:<8}4m Δ{:<8}5m Δ{:<8}7m Δ{:<8}9m Δ{:<8}11m Δ{:<7}13m Δ{:<7}'.format('','','','','','','','','','','',''))


		# Debug 
		# print(f'ʕಠಿᴥಠʔ Tickers are {tickers} --- Type: {type(tickers)} --- Length: {len(tickers)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {volume} --- Type: {type(volume)} --- Length: {len(volume)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {rvol} --- Type: {type(rvol)} --- Length: {len(rvol)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL Current is {rvol_total} --- Type: {type(rvol_total)} --- Length: {len(rvol_total)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL 30s is {rvol_30s} --- Type: {type(rvol_30s)} --- Length: {len(rvol_30s)}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL 60s is {rvol_60s} --- Type: {type(rvol_60s)} --- Length: {len(rvol_60s)}\n')

		# Wait
		wait_seconds = 30
		elapsed_minutes = ((len(rvol['history'])-1) * wait_seconds) / 60 
		for i in range(0, wait_seconds+1):
			stdout.write('\r')
			stdout.write(f'{elapsed_minutes} Minutes Elapsed. Updating in {wait_seconds-i} Seconds...')
			stdout.flush()
			sleep(1)
		print('\n\nWorking...\n')