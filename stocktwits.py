from argparse import ArgumentParser
import requests
import json
import csv

BASE_URL = 'https://api.stocktwits.com/api/2/'
ap = ArgumentParser()
ap.add_argument('-t', '--trending', action='store_true')
ap.add_argument('-s', '--scanner', action='store_true')

args = vars(ap.parse_args())
print(f'args --- {args}\n')


if args['trending']:
		url = BASE_URL + 'trending/symbols.json'
		r = requests.get(url)
		dict_str = r.content.decode("UTF-8")
		symbols = json.loads(dict_str)['symbols']
		# print(f'ᶘಠᴥಠᶅ {type(symbols)} --- {symbols}')

		for symbol in symbols:
			print(f'{symbol["symbol"]}')

		with open('stocktwits_trending.tsv', 'w') as out_file:
			tsv_writer = csv.writer(out_file, delimiter='\t')
			for item in ordered_symbol_count.items():
				tsv_writer.writerow([item[0], item[1]])


if args['scanner']:
	users = ['acinvestorblog', 'mrinvestorpro', 'lukeam',
			'ProfessorDman1', 'tradexlnc', 'TeamRVR', 'harmongreg',
			'DekmarTrades', 'SwingThinKing', 'Mrs_BlackInkEconomics',
			'WallStJesus', 'PLATINUM_TRADES', 'BARNIMAL_',
			'Dark_Prince', 'ProfitsInYards', 'JSP_Dilution_Player',
			'StockAuthority', 'RainxMaker', 'CycleTrade', 'CamTheMan_',
			'BRJP_CALLS', 'Vestorinvest', 'Invest2live', 'FonsieTrader',
			'iBuyHighSellLow_', 'DaBullRunner',
			]

	if args['scanner']:
		symbol_count = {}

		for index, user in enumerate(users):
			print(f'ᶘಠᴥಠᶅ {index} --- {user}')
			# if index >= 2:
			# 	break
			
			url = BASE_URL + f'streams/user/{user}.json'
			r = requests.get(url)
			dict_str = r.content.decode("UTF-8")
			messages = json.loads(dict_str)['messages']

			for m in messages:
				if 'symbols' in m:
					for d in m['symbols']:

						ticker = d['symbol']
						print(ticker)

						if ticker in symbol_count:
							symbol_count[ticker] += 1
						else:
							symbol_count[ticker] = 1 


		ordered_symbol_count = dict(sorted(symbol_count.items(), key=lambda item:item[1], reverse=True))
		# for item in ordered_symbol_count.items():
		# 	print(item)

		with open('stocktwits_scanner.tsv', 'w') as out_file:
			tsv_writer = csv.writer(out_file, delimiter='\t')
			for item in ordered_symbol_count.items():
				tsv_writer.writerow([item[0], item[1]])