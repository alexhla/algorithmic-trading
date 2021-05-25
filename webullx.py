from argparse import ArgumentParser
from webull import webull
import config

wb = webull()
wb._access_token = config.WEBULL_ACCESS_TOKEN

ap = ArgumentParser()
ap.add_argument('-gma', '--get_mfa', action='store_true')
ap.add_argument('-gsq', '--get_security_question', action='store_true')
ap.add_argument('-gat', '--get_access_token', action='store_true')
ap.add_argument('-rat', '--refresh_access_token', action='store_true')


ap.add_argument('-ga', '--get_analysis', nargs=1, metavar=['TICKER'])
ap.add_argument('-gcf', '--get_capital_flow', nargs=1, metavar=['TICKER'])
ap.add_argument('-geh', '--get_etf_holding', nargs=1, metavar=['TICKER'])
ap.add_argument('-gih', '--get_institutional_holding', nargs=1, metavar=['TICKER'])

ap.add_argument('-gf', '--get_financials', nargs=1, metavar=['TICKER'])
ap.add_argument('-gsi', '--get_short_interest', nargs=1, metavar=['TICKER'])





ap.add_argument('-gco', '--get_current_orders', action='store_true')
ap.add_argument('-gba', '--get_bid_ask', nargs=1, metavar=['TICKER'])
ap.add_argument('-to', '--test_order', nargs=1, metavar=['TICKER'])
ap.add_argument('-po', '--place_order', nargs=1, metavar=['TICKER'])

args = vars(ap.parse_args())
print(f'args --- {args}\n')

'''

Get MFA Code

'''

if args['get_mfa']:
	wb.get_mfa(config.WEBULL_EMAIL)

'''

Get Security Question

'''

if args['get_security_question']:
	response = wb.get_security(config.WEBULL_EMAIL)
	# response = wb.next_security(config.WEBULL_EMAIL)
	print(response)

'''

Get Access Token

'''


if args['get_access_token']:
	print(f'ᶘಠᴥಠᶅ Getting Access Token')
	response = wb.login(config.WEBULL_EMAIL, config.WEBULL_PASSWORD, 'scribot', 
		config.WEBULL_VCODE, config.WEBULL_QUESTION_ID, config.WEBULL_QUESTION_ANSWER)
	print(response)

'''

Refresh Access Token

'''

if args['refresh_access_token']:
	print(f'ᶘಠᴥಠᶅ Rereshing Access Token')
	wb._refresh_token = config.WEBULL_REFRESH_TOKEN
	wb._access_token = config.WEBULL_ACCESS_TOKEN
	wb._token_expire = config.WEBULL_TOKEN_EXPIRE
	wb._uuid = config.WEBULL_UUID
	response = wb.refresh_login()
	print(response)





'''

Get Analysis

'''

if args['get_analysis']:
	ticker = args['get_analysis'][0]
	analysis = wb.get_analysis(stock=ticker)
	print(f'ᶘಠᴥಠᶅ Analysis is {analysis}')



'''

Get Capital Flow

'''

if args['get_capital_flow']:
	ticker = args['get_capital_flow'][0]
	capital_flow = wb.get_capital_flow(stock=ticker)
	print(f'ᶘಠᴥಠᶅ Capital Flow is {capital_flow}')




'''

Get ETF Holding

'''

if args['get_etf_holding']:
	ticker = args['get_etf_holding'][0]
	etf_holding = wb.get_etf_holding(stock=ticker)
	print(f'ᶘಠᴥಠᶅ ETF Holding is {etf_holding}')





'''

Get Institutional Holding

'''

if args['get_institutional_holding']:
	ticker = args['get_institutional_holding'][0]
	institutional_holding = wb.get_institutional_holding(stock=ticker)
	print(f'ᶘಠᴥಠᶅ Institutional Holding is {institutional_holding}')





'''

Get Financials

'''

if args['get_financials']:
	ticker = args['get_financials'][0]
	financials = wb.get_financials(stock=ticker)
	# print(f'ᶘಠᴥಠᶅ Financials is {financials}')

	for f in financials:
		for item in financials[f]:
			print(f'{item}\n\n')



'''

Get Short Interest

'''

if args['get_short_interest']:
	ticker = args['get_short_interest'][0]
	short_interest = wb.get_short_interest(stock=ticker)
	print(f'ᶘಠᴥಠᶅ Short Interest Holding is {short_interest}')




'''

Get Current Orders

'''

if args['get_current_orders']:
	response = wb.get_current_orders()
	for order in response:
		symbol = order['ticker']['symbol']
		orderType = order['orderType']
		action = order['action']
		lmtPrice = order['lmtPrice']
		print(f'{orderType} {action} {symbol}\t{lmtPrice}')
		



'''

Get Bid Ask

'''

if args['get_bid_ask']:
	ticker = args['get_bid_ask'][0]
	quote = wb.get_quote(stock=ticker)
	print(f'ᶘಠᴥಠᶅ Quote is {quote}')

	ask_price = float(quote['depth']['ntvAggAskList'][0]['price'])
	bid_price = float(quote['depth']['ntvAggBidList'][0]['price'])
	order_price = round((bid_price + ask_price) / 2, 2)
	print(f'ᶘಠᴥಠᶅ {ticker} Ask Price: {ask_price}')
	print(f'ᶘಠᴥಠᶅ {ticker} Mid Price: {order_price}')
	print(f'ᶘಠᴥಠᶅ {ticker} Bid Price: {bid_price}')



'''

Test Order

'''

if args['test_order']:
	ticker = args['test_order'][0]


	id_response = wb.get_account_id()
	token_response = wb.get_trade_token(config.WEBULL_TRADE_TOKEN)
	# print(f'ᶘಠᴥಠᶅ ID Response is {id_response}')
	# print(f'ᶘಠᴥಠᶅ Token Response is {token_response}')

	quote = wb.get_quote(stock=ticker)
	# print(f'ᶘಠᴥಠᶅ Quote is {quote}')

	ask_price = float(quote['depth']['ntvAggAskList'][0]['price'])
	bid_price = float(quote['depth']['ntvAggBidList'][0]['price'])
	order_price = 1
	# order_price = round((bid_price + ask_price) / 2, 2)
	print(f'ᶘಠᴥಠᶅ {ticker} Ask Price: {ask_price}')
	print(f'ᶘಠᴥಠᶅ {ticker} Bid Price: {bid_price}')
	print(f'ᶘಠᴥಠᶅ Order Price: {order_price}')

	qty = 1
	print(f'Buying {qty} Shares of {ticker} at {order_price}')

	response = wb.place_order(stock=ticker, price=order_price, action='BUY', orderType='LMT', enforce='GTC', quant=qty)
	print(f'Broker Response {response}')




'''

Place Order

'''

if args['place_order']:
	ticker = args['place_order'][0]
	
	id_response = wb.get_account_id()
	token_response = wb.get_trade_token(config.WEBULL_TRADE_TOKEN)
	# print(f'ᶘಠᴥಠᶅ ID Response is {id_response}')
	# print(f'ᶘಠᴥಠᶅ Token Response is {token_response}')

	quote = wb.get_quote(stock=ticker)
	# print(f'ᶘಠᴥಠᶅ Quote is {quote}')
	ask_price = float(quote['depth']['ntvAggAskList'][0]['price'])
	bid_price = float(quote['depth']['ntvAggBidList'][0]['price'])
	# order_price = bid_price
	order_price = round((bid_price + ask_price) / 2, 2)
	print(f'ᶘಠᴥಠᶅ {ticker} Ask Price: {ask_price}')
	print(f'ᶘಠᴥಠᶅ {ticker} Bid Price: {bid_price}')
	print(f'ᶘಠᴥಠᶅ Order Price: {order_price}')

	qty = int(5000/order_price)
	print(f'Buying {qty} Shares of {ticker} at {order_price}')

	response = wb.place_order(stock=ticker, price=order_price, action='BUY', orderType='LMT', enforce='GTC', quant=qty)
	print(f'Broker Response {response}')