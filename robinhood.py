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

	selection = 'microcap_float10M_price10USD'
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

	selection = 'foobar'
	tickers = watchlists.tickers[selection]
	volume_history = get_volume_history_maximums(selection)	
	volume = []
	rvol = []
	query_size = 75
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])


	while True:
		ranked_rvol = []
		ranked_5min_week = []
		ranked_hour_month = []

		# Get Current Volume
		temp = []
		for q in query_list:
			fundementals = r.stocks.get_fundamentals(q)
			for f in fundementals:
				temp.append({key: f[key] for key in f.keys() & {'volume', 'average_volume'}})

		# Convert to Data Frame and Compute RVOL 
		df = DataFrame.from_dict(temp)
		df['RVOL'] = df['volume'].astype(float) / df['average_volume'].astype(float)

		# Log Volume and RVOL
		volume.append(df['volume'].astype(float).tolist())
		rvol.append(df['RVOL'].tolist())

		if len(volume) > 1 :
			for i in range(len(tickers)):

				vdelta = round(volume[-1][i] - volume[-2][i], 3)
				v_5min_week = round(volume_history[tickers[i]][0] / 10, 3)
				v_hour_month = round(volume_history[tickers[i]][1] / 120, 3)

				ranked_5min_week.append((tickers[i], vdelta / v_5min_week))
				ranked_hour_month.append((tickers[i], vdelta / v_hour_month))
				ranked_rvol.append((tickers[i], round(rvol[-1][i], 3)))

			# Sort
			ranked_rvol.sort(key=lambda x:x[1])
			ranked_5min_week.sort(key=lambda x:x[1])
			ranked_hour_month.sort(key=lambda x:x[1])

			# Display Results
			print('RVOL{:<14}5min/Week{:<9}hour/month'.format(' ', ' '))
			for i in range(0, len(tickers)):
				print(f'{ranked_rvol[i][0]:<6}{ranked_rvol[i][1]:<12}{ranked_5min_week[i][0]:<6}{ranked_5min_week[i][1]:<12}{ranked_hour_month[i][0]:<6}{ranked_hour_month[i][1]:<12}')

		# Debug 
		# print(f'ʕಠಿᴥಠʔ Tickers are {data["ticker"]} {type(data["ticker"])}\n')
		# print(f'ʕಠಿᴥಠʔ Ticker Count is {len(data["ticker"])}\n')
		# print(f'ʕಠಿᴥಠʔ Request is {request} {type(request)}\n')
		# print(f'ʕಠಿᴥಠʔ df is {df} {type(df)}\n')
		# print(f'ʕಠಿᴥಠʔ Fundementals are {fundementals} {type(fundementals)}\n')
		# print(f'ʕಠಿᴥಠʔ Data is {data} {type(data)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {data["volume"]} {type(data["volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {volume} {type(volume)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {temp} {type(temp)}\n')	
		# print(f'ʕಠಿᴥಠʔ Volume Count is {len(data["volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Volume History\n{volume_history}\n')
		# print(f'ʕಠಿᴥಠʔ Average Volume is {data["average_volume"]} {type(data["average_volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Average Volume Count is {len(data["average_volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {data["RVOL"]} {type(data["RVOL"])}\n')
		# print(f'ʕಠಿᴥಠʔ rvol is {rvol} {type(rvol)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume Increase Rank is {volume_increase_rank} {type(volume_increase_rank)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume vs 5min/Week Rank is {volume_vs_5min_week_max} {type(volume_vs_5min_week_max)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume vs hour/month Rank is {volume_vs_hour_month_max} {type(volume_vs_hour_month_max)}\n')		
		# for key in data:
		# 	print(f'ʕಠಿᴥಠʔ {key} {len(data[key])}')

		# Wait
		wait_seconds = 30
		for i in range(0, wait_seconds+1):
			stdout.write('\r')
			stdout.write(f'Updating in {wait_seconds-i} Seconds...')
			stdout.flush()
			sleep(1)
		print('\n\nWorking...\n')