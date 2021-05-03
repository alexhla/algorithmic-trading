from argparse import ArgumentParser
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

# import robin_stocks as r  # package name differs with version
import robin_stocks.robinhood as r

# local imports
import config

# Login to Robinhood
r.login(config.ROBINHOOD_EMAIL, config.ROBINHOOD_PASSWORD)

# Instantiate the argument parser object
ap = ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-i', '--info', nargs='+', metavar=['TICKERS'],
	help='')

ap.add_argument('-rvol', '--relative_volume_scanner', nargs=1, metavar=['INTERVAL'],
	help='')

# Parse user arguments
args = vars(ap.parse_args())
print(f'args --- {args}\n')

if args['relative_volume_scanner']:

	def animate(i):
		fundementals = r.stocks.get_fundamentals(tickers)
		df = pd.DataFrame.from_dict(fundementals)
		df['rvol'] = df['volume'].astype(float) / df['average_volume'].astype(float)
		rvol.append(df['rvol'].round(decimals=3).tolist())
		ax1.clear()
		ax1.plot(rvol)
		ax1.set_xticks([])
		ax1.legend(tickers, bbox_to_anchor=(1.05, 0.5), loc='center')
		# print(f'ʕ•ᴥ•ʔ Tickers \t {tickers}\n')
		# print(f'ʕ•ᴥ•ʔ RVOL \t {rvol}\n')
		# print(dir(ax1))

	interval = int(args['relative_volume_scanner'][0])
	rvol = []
	tickers = ['PXS', 'NLSP', 'EVK', 'JOB', 'AEI', 
			'SEAC', 'CREG', 'AHPI', 'WNW', 'MDRR',
			'CASI', 'ASTC', 'WIMI', 'EVFM', 'MDLY',
			'BTX',]

	plt.style.use('seaborn-dark')
	fig = plt.figure(figsize=(12, 8))
	fig.canvas.set_window_title(f'RVOL Scanner  |  {interval} Second Interval')
	ax1 = fig.add_subplot(1,1,1)
	handle = animation.FuncAnimation(fig, animate, interval=(interval*1000))
	plt.show()









if args['info']:

	tickers = args['info']
	data = {'tickers':tickers}

	# Get Stock Exchange MIC Code
	instrument = r.stocks.find_instrument_data(tickers)
	data['stock_exchange'] = instrument[0]['market'].split('/')[-2]

	# Convert MIC Code to Exchange Name
	if data['stock_exchange'] == 'XNYS':
		data['stock_exchange'] = ' '.join((data['stock_exchange'], '(NYSE)'))
	if data['stock_exchange'] == 'XNAS':
		data['stock_exchange'] = ' '.join((data['stock_exchange'], '(NASDAQ)'))
	if data['stock_exchange'] == 'XASE':
		data['stock_exchange'] = ' '.join((data['stock_exchange'], '(AMEX)'))

	# Get Lastest Trade Price
	latest_price = r.stocks.get_latest_price(tickers, priceType=None, includeExtendedHours=True)
	data['latest_price'] = round(float(latest_price[0]), 2)

	# Get Market Cap, Volume, Shares, and Float
	fundementals = r.stocks.get_fundamentals(tickers)
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