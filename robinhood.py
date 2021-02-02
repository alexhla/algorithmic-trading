from argparse import ArgumentParser
from time import time
import datetime
import csv

import matplotlib.pyplot as plt
import robin_stocks as r
import pandas as pd

# local imports
import config

# Begin timing of script response time
tic = time()

# Login to Robinhood
r.login(config.ROBINHOOD_EMAIL, config.ROBINHOOD_PASSWORD)

# Instantiate the argument parser object
ap = ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-sbox', '--sandbox', action='store_true',
	help='sandbox is for running prototype code and tests')

ap.add_argument('-acctinfo', '--account_info',  action='store_true',
	help='Prints account information to terminal')

ap.add_argument('-cryptoinfo', '--crypto_info',  action='store_true',
	help='Prints account information to terminal')

ap.add_argument('-stockinfo', '--stock_info',  action='store_true',
	help='Prints account information to terminal')


# Parse user arguments
args = vars(ap.parse_args())
print(f'args --- {args}\n')



tickers = []

args['readcsv'] = True
if args['readcsv']:
	with open('schwabstocks.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for index, row in enumerate(csv_reader):
			if index == 0:
				pass
			elif index == 5:
				pass
			else:
				tickers.append(row)


if args['stock_info']:

	stock_data = r.stocks.get_stock_historicals('AMC', interval='5minute', span='day')

	df = pd.DataFrame.from_dict(stock_data)
	fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(16,10))
	df['close_price'].astype(float).plot(ax=axes[0])	
	plt.show()#block=False)




	# for stock in stock_data:
	# 	# data = pd.DataFrame.from_dict(stock, index=[0])
	# 	print(stock)

















if args['account_info']:
	print('\n--------------------- Account Profile --------------------\n')
	account_profile = r.profiles.load_account_profile(info=None)
	for k,v in account_profile.items():
		if k in ['margin_balances', 'instant_eligibility']:
			print(f'{k}')
			for x,y in v.items():
				print('{0:45}{1}'.format(x,y))
		else:
			print("{0:45}{1}".format(k,v))

	print('\n-------------------- Portfolio Profile -------------------\n')
	portfolio_profile = r.profiles.load_portfolio_profile(info=None)
	for k,v in portfolio_profile.items():
		print("{0:45}{1}".format(k,v))


	print('\n-------------------- Crypto Positions --------------------\n')
	crypto_positions = r.crypto.get_crypto_positions(info=None)
	crypto_ids = []

	for crypto_position in crypto_positions:
		for k,v in crypto_position.items():
			if k == 'cost_bases':
				print(f'{k}')
				for element in v:
					for x,y in element.items():
						print('{0:25}{1}'.format(x,y))
			elif k == 'currency':
				print(f'{k}')
				for x,y in v.items():
					print('{0:25}{1}'.format(x,y))	
			else:
				print("{0:25}{1}".format(k,v))



if args['crypto_info']:
	print('\n--------------------- Crypto Quotes ---------------------\n')
	crypto_quote = r.crypto.get_crypto_quote('DOGE', info=None)
	for k,v in crypto_quote.items():
		print('{0:15}{1}'.format(k,v))




	print('\n------------------- Crypto Historicals -------------------\n')

	crypto_historicals = r.crypto.get_crypto_historicals('DOGE', interval='5minute', span='day', bounds='24_7', info=None)
	stock_data = pd.DataFrame.from_dict(crypto_historicals)
	# print(stock_data)

	for window in [10, 20, 30, 50]:
		stock_data['MA'+str(window)] = stock_data['close_price'].rolling(window=window).mean()
		stock_data['20dSTD_MA'+str(window)] = stock_data['close_price'].rolling(window=window).std()
		stock_data['Upper_MA'+str(window)] = stock_data['MA'+str(window)] + (stock_data['20dSTD_MA'+str(window)] * 2)
		stock_data['Lower_MA'+str(window)] = stock_data['MA'+str(window)] - (stock_data['20dSTD_MA'+str(window)] * 2)		





	fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(16,10))
	stock_data['close_price'].astype(float).plot(ax=axes[0])	
	stock_data[['MA10','Upper_MA10','Lower_MA10']].plot(ax=axes[1])
	stock_data[['MA20','Upper_MA20','Lower_MA20']].plot(ax=axes[2])
	# stock_data[['MA30','Upper_MA30','Lower_MA30']].plot(ax=axes[3])
	# stock_data[['MA50','Upper_MA50','Lower_MA50']].plot(ax=axes[3])
	plt.show()#block=False)
	# plt.pause(3)
	# plt.close()




# End timing of script response time
toc = time()
print(f'\nElapsed time is {round((toc - tic), 2)} seconds')





### DEBUGING CODE ###

# print(f'k is type {type(k)}')

# print(f'k is len {len(k)}')

# for column in stock_data.columns:
# 	print(column)