from argparse import ArgumentParser
from datetime import datetime
from time import sleep
from sys import stdout
import requests
import json

BASE_URL = 'https://api.stocktwits.com/api/2/'
ap = ArgumentParser()
ap.add_argument('-mipscan', '--mrinvestorpro_scanner', action='store_true')


args = vars(ap.parse_args())
print(f'args --- {args}\n')

'''

mrinvestorpro Scanner

'''

if args['mrinvestorpro_scanner']:

	while True:
		interval = 20
		url = BASE_URL + 'streams/user/mrinvestorpro.json'
		r = requests.get(url)
		dict_str = r.content.decode("UTF-8")
		messages = json.loads(dict_str)['messages']
		timestamp = datetime.now().replace(second=0, microsecond=0)
		m_timestamp = datetime.fromisoformat(messages[0]['created_at'][:-1]).replace(second=0, microsecond=0)
		print(f'ᶘಠᴥಠᶅ The Current Time  \t {timestamp}')
		print(f'ᶘಠᴥಠᶅ Last Message Time \t {m_timestamp}\n')
		print(f'ᶘಠᴥಠᶅ Last Message \t {messages[0]["body"]}\n')
		if timestamp == m_timestamp:
				if messages[0]['body'][0] != '@':
					if any(x in m['body'] for x in ['alert', 'Alert', 'ALERT']):
						unicode_chars = []
						for char in m['body'][:30]:
							unicode_chars.append(ord(char))
							# print(f'ᶘಠᴥಠᶅ {char} \t {ord(char)}')
						emoji_siren_value = 128680
						emoji_siren_count = unicode_chars.count(emoji_siren_value) 
						if emoji_siren_count > 1:
							print(m['body'])
							print(f'Emoji Siren Count is {emoji_siren_count}')
							
							ticker = ''
							for index, char in enumerate(m['body']):
								if index == 0:
									pass
								elif char == ' ':
									break
								else:
									ticker = ticker + char

							print(f'Placing Trade for {ticker}')

		# Wait
		for i in range(0, interval+1):
			stdout.write('\r')
			stdout.write(f'Updating in {interval-i} Seconds...')
			stdout.flush()
			sleep(1)
		print('\nScanning...\n')