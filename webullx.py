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
ap.add_argument('-gco', '--get_current_orders', action='store_true')
ap.add_argument('-por', '--place_order', nargs=1, metavar=['TICKER'])

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

Place Order

'''

if args['place_order']:
	ticker = args['place_order'][0]
	quote = wb.get_quote(stock=ticker)
	# print(f'ᶘಠᴥಠᶅ Quote is {quote}')

	ask_price = float(quote['depth']['ntvAggAskList'][0]['price'])
	bid_price = float(quote['depth']['ntvAggBidList'][0]['price'])
	order_price = round(bid_price - (bid_price*0.01), 2)
	print(f'ᶘಠᴥಠᶅ {ticker} Ask Price: {ask_price}')
	print(f'ᶘಠᴥಠᶅ {ticker} Bid Price: {bid_price}')
	print(f'ᶘಠᴥಠᶅ Order Price: {order_price}')

	id_response = wb.get_account_id()
	token_response = wb.get_trade_token(config.WEBULL_TRADE_TOKEN)
	# print(f'ᶘಠᴥಠᶅ ID Response is {id_response}')
	# print(f'ᶘಠᴥಠᶅ Token Response is {token_response}')

	qty = int(6300/order_price)
	print(f'Buying {qty} Shares of {ticker} at {order_price}')
	response = wb.place_order(stock=ticker, price=order_price, action='BUY', orderType='LMT', enforce='GTC', quant=qty)
	print(response)
