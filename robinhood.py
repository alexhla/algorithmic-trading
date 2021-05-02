from argparse import ArgumentParser
import datetime
import csv
import pandas as pd
import robin_stocks as r  # package name differs with version
# import robin_stocks.robinhood as r

# local imports
import config

# Login to Robinhood
r.login(config.ROBINHOOD_EMAIL, config.ROBINHOOD_PASSWORD)

# Instantiate the argument parser object
ap = ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-i', '--info', nargs=1, metavar=['TICKER'],
	help='')

ap.add_argument('-w', '--window', nargs=3, metavar=['TICKER', 'START_DATE', 'END_DATE'],
	help='')

# Parse user arguments
args = vars(ap.parse_args())
print(f'args --- {args}\n')

if args['window']:
	print('Hello World')
	pass




if args['info']:

	ticker = args['info'][0]
	data = {'ticker':ticker}

	# Get Stock Exchange MIC Code
	instrument = r.stocks.find_instrument_data(ticker)
	data['stock_exchange'] = instrument[0]['market'].split('/')[-2]

	# Convert MIC Code to Exchange Name
	if data['stock_exchange'] == 'XNYS':
		data['stock_exchange'] = ' '.join((data['stock_exchange'], '(NYSE)'))
	if data['stock_exchange'] == 'XNAS':
		data['stock_exchange'] = ' '.join((data['stock_exchange'], '(NASDAQ)'))
	if data['stock_exchange'] == 'XASE':
		data['stock_exchange'] = ' '.join((data['stock_exchange'], '(AMEX)'))

	# Get Lastest Trade Price
	latest_price = r.stocks.get_latest_price(ticker, priceType=None, includeExtendedHours=True)
	data['latest_price'] = round(float(latest_price[0]), 2)

	# Get Market Cap, Volume, Shares, and Float
	fundementals = r.stocks.get_fundamentals(ticker)
	df = pd.DataFrame.from_dict(fundementals)
	for col in df.columns:
		if any(word in col for word in ['market_cap', 'volume', 'shares', 'float']):
			data[col] = round(float(df[col][0]), 2)

	# Compute Data
	data['RVOL'] = round(data['volume'] / data['average_volume'], 2)
	data['RVOL_2_weeks'] = round(data['volume'] / data['average_volume_2_weeks'], 2)

	# Print Data 
	for k,v in data.items():
		print(f'{k:<25}{v}')
