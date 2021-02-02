import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

# local imports
import config

# Instantiate the argument parser object
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-tickers', '--ticker_symbols', nargs='+', required=True, metavar=('TICKER_SYBMOLS'), help='ticker symbols')
ap.add_argument('-time', '--time_frame', nargs=1, metavar=('TIME_FRAME'), help='ticker symbols')

# parse user arguments
args = vars(ap.parse_args())

print(args)

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365)
print(f'start date is {start_date}\nend date is {end_date}')


#define the ticker symbol
tickerSymbols = ['CAL', 'TSLA']



#get the historical prices for tickers
for symbol in tickerSymbols:
	#get data on this ticker
	tickerData = yf.Ticker(symbol)
	tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)

	print(tickerDf)