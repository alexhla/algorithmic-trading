from argparse import ArgumentParser
from datetime import datetime
from pandas import DataFrame
from time import sleep
from sys import stdout
from csv import writer

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

ap.add_argument('-hec', '--history_endpoint_checker', action='store_true',
	help='')

ap.add_argument('-rvol', '--rvol_scanner', nargs=1, metavar=['INTERVAL'],
	help='')

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

History Endpoint Checker

'''
if args['history_endpoint_checker']:

	selection = 'ten_random_tickers_for_test'
	tickers = stockdictionary.tickers[selection]

	for t in tickers:
		print(f'{t}')
		historicals = r.stocks.get_stock_historicals(t, interval='5minute', span='week')
		print(historicals)



'''

RVOL Scanner

'''

if args['rvol_scanner']:

	selection = 'ten_random_tickers_for_test'
	timestamp = f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}-{selection.replace("_", "-")}'
	tickers = stockdictionary.tickers[selection]
	interval = int(args['rvol_scanner'][0])	
	volume_history_5min_1week = {}
	volume = []
	rvol = []
	query_size = 75
	query_list = []
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

	# Get Volume History
	temp_list = []
	for i, q in enumerate(query_list):
		print(f'Requesting Query List {i+1} of {len(query_list)}')
		historicals = r.stocks.get_stock_historicals(q, interval='5minute', span='week')
		for h in historicals:
			temp_list.append({key: h[key] for key in h.keys() & {'begins_at', 'symbol', 'volume', 'session'}})
	df = DataFrame.from_dict(temp_list)

	# Calculate Mean, Median, Standard Dev, Min, Max
	for t in tickers:
		volume_history_5min_1week[t] = df[df["symbol"] == t].describe().to_dict()['volume']

	# Save Volume Mean TSV File
	volume_history_filepath  = f'data/{timestamp}-5min-1week-volume-average.tsv'	
	with open(volume_history_filepath, 'w+') as out_file:
		tsv_writer = writer(out_file, delimiter='\t')
		for k,v in volume_history_5min_1week.items():
			tsv_writer.writerow((k, int(v['mean'])))	

	# Init RVOL TSV File	
	rvol_filepath  = f'data/{timestamp}-interval{interval}s-rvol.tsv'	
	with open(rvol_filepath, 'w+') as out_file:
		tsv_writer = writer(out_file, delimiter='\t')
		tsv_writer.writerow(tickers)

	# Main Loop
	while True:
		ticker_rvol_pairs = []

		# Get Current Volume
		for q in query_list:
			fundementals = r.stocks.get_fundamentals(q)
			for f in fundementals:
				volume.append({key: f[key] for key in f.keys() & {'volume', 'average_volume'}})

		# Compute RVOL
		df = DataFrame.from_dict(volume)
		df['RVOL'] = df['volume'].astype(float) / df['average_volume'].astype(float)
		rvol.append(df['RVOL'].tolist())

		# Update TSV File
		with open(rvol_filepath, 'a') as out_file:
			tsv_writer = writer(out_file, delimiter='\t')
			tsv_writer.writerow(rvol[-1])

		# Generate List of (Ticker, RVOL) Tuple Pairs for Sorting
		for i in range(len(tickers)):
			if tickers[i] not in stockdictionary.tickers['blacklist']:
				ticker_rvol_pairs.append((tickers[i], rvol[-1][i]))
		ticker_rvol_pairs.sort(key=lambda x:x[1])

		# Display Results
		if len(rvol) > 1:
			# for x in ticker_rvol_pairs:
			# 	print(f'{x[0]:<6}{round(x[1],3)}')
			# stdout.write('\n')
		# else:
			df = DataFrame.from_dict(rvol)
			print(df)

		# Debug 
		# print(f'ʕಠಿᴥಠʔ Tickers are {data["ticker"]} {type(data["ticker"])}\n')
		# print(f'ʕಠಿᴥಠʔ Ticker Count is {len(data["ticker"])}\n')
		# print(f'ʕಠಿᴥಠʔ Request is {request} {type(request)}\n')
		# print(f'ʕಠಿᴥಠʔ df is {df} {type(df)}\n')
		# print(f'ʕಠಿᴥಠʔ Fundementals are {fundementals} {type(fundementals)}\n')
		# print(f'ʕಠಿᴥಠʔ Data is {data} {type(data)}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {data["volume"]} {type(data["volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Volume is {volume} {type(volume)}\n')			
		# print(f'ʕಠಿᴥಠʔ Volume Count is {len(data["volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Average Volume is {data["average_volume"]} {type(data["average_volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ Average Volume Count is {len(data["average_volume"])}\n')
		# print(f'ʕಠಿᴥಠʔ RVOL is {data["RVOL"]} {type(data["RVOL"])}\n')
		# print(f'ʕಠಿᴥಠʔ rvol is {rvol} {type(rvol)}\n')			
		# for key in data:
		# 	print(f'ʕಠಿᴥಠʔ {key} {len(data[key])}')

		# Wait
		for i in range(0, interval+1):
			stdout.write('\r')
			stdout.write(f'Updating in {interval-i} Seconds...')
			stdout.flush()
			sleep(1)
		print('\n\nWorking...\n')

