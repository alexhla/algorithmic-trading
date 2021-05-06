from argparse import ArgumentParser
from sys import stdout
from datetime import datetime
import time
import csv
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
	df = pd.DataFrame.from_dict(data)
	df['RVOL'] = df['volume'].astype(float) / df['average_volume'].astype(float)

	# Display Results
	for index, row in df.iterrows():
		print(f'{row}\n')



if args['rvol_scanner']:

	interval = int(args['rvol_scanner'][0])
	selection = 'microcap_float10M_price10USD'
	tickers = stockdictionary.tickers[selection]
	query_size = 100
	query_list = []

	# Build Query List
	for i in range(0, len(tickers), query_size):
		query_list.append(tickers[i:i+query_size])

	# Init TSV File
	tsv_filepath  = f'data/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}-{selection.replace("_", "-")}-interval{interval}.tsv'	
	with open(tsv_filepath, 'w+') as out_file:
		tsv_writer = csv.writer(out_file, delimiter='\t')
		tsv_writer.writerow(tickers)

	# Main Loop
	while True:
		volume = []
		rvol = []
		data= []

		# Get Volume
		for q in query_list:
			fundementals = r.stocks.get_fundamentals(q)
			for f in fundementals:
				volume.append({key: f[key] for key in f.keys() & {'volume', 'average_volume'}})

		# Compute RVOL
		df = pd.DataFrame.from_dict(volume)
		df['RVOL'] = df['volume'].astype(float) / df['average_volume'].astype(float)
		rvol = df['RVOL'].tolist()

		# Update TSV File
		with open(tsv_filepath, 'a') as out_file:
			tsv_writer = csv.writer(out_file, delimiter='\t')
			tsv_writer.writerow(rvol)

		# Generate List of (Ticker, RVOL) Tuple Pairs for Sorting
		for i in range(len(tickers)):
			if tickers[i] not in stockdictionary.tickers['blacklist']:
				data.append((tickers[i], rvol[i]))
		data.sort(key=lambda x:x[1])

		# Display Results
		for x in data:
			print(f'{x[0]:<6}{round(x[1],3)}')
		stdout.write('\n')

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
			time.sleep(1)
		print('\n\nWorking...\n')