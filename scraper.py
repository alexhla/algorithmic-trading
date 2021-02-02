import sys
import time
import praw
import numpy as np
import pandas as pd
import argparse
import requests
import subprocess
import lxml.html
from lxml import etree



# Local imports
import config

# Begin timing of script response time
tic = time.time()

# Instantiate the argument parser object
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-sbox', '--sandbox', action='store_true',
	help='sandbox is for running prototype code and tests')

ap.add_argument('-all', '--scrape_all',  action='store_true',
	help='Calls all scrapers i.e. -reddit -thelion -')

ap.add_argument('-topstonks', '--topstonks_trending_stocks_scraper',  action='store_true',
	help='Scrapes the front page of topstonks.com for trending stocks')

ap.add_argument('-thelion', '--thelion_wall_street_pit_scraper',  action='store_true',
	help='Scrapes the first 25 forum posts on WallStreetPit TheLion.com for its associated stock ticker')

ap.add_argument('-stockaholics', '--stockaholics_forum_scraper',  action='store_true',
	help='Scrapes the forum of stockaholics.com')

ap.add_argument('-reddit', '--reddit_title_ticker_scraper', nargs='+', metavar=['NUMBER_OF_POSTS_TO_SCAN', 'DURATION', 'SUBREDDITS'],
	help='Scrapes any number of reddit SUBREDDITS for both TOP DURATION and HOT posts for any NUMBER_OF_POSTS_TO_SCAN')

ap.add_argument('-valueforum', '--value_forum_scraper',  nargs=1, metavar=['NUMBER_OF_POSTS_TO_SCAN'],
	help='Scrapes the forum of valueforum.com')

# Parse user arguments
args = vars(ap.parse_args())
# print(f'\nargs --- {args}\n')




'''

Utility Functions

camelCaseNames are local function names

UPPER_CASE_NAMES are local variables specific to each local function

'''

def convertDictToPandasDataFrame(d):
	# d.keys() -----> column
	# d.values() ---> list(data)
	# pd.Series inputs NaN for empty locations to avoid error
	# .fillna("") replaces NaN with empty string for readability
	return pd.DataFrame(dict([(k,pd.Series(v, dtype='object')) for k,v in d.items()])).fillna("")


def checkIfWordIsTicker(word):
	if not isinstance(word, str):
		return False

	BLACKLISTED_WORDS = {'I','A',
	'IN','TO','DD','FD','EU','IV','IS','US','OF','BE','AT','GO','WE','UP',
	'ON','NO','BY','IT','DO','IM','RH','SO',
	'THE','NOT','NEW','AND','FOR','BIG','WSB','API','CAN','YOU','ARE','ALL','WHY','GET',
	'ITM','OTM','ETF','IPO','ROI','SEC','USD','USA','IRA','LET','OUT','BUY','MOD',
	'CEO','CFO','MOD','AOC','ONE','HAS','ARK','OUR','NOW',
	'CNBC','ELON','THIS','SPAC','HOLD','PUTS','PMCC','YOLO','LETS','STOP','THEY','NEWS',
	'MOON','KEEP','FAKE','YOUR','JUST','DONT','LIKE','FALL','FUCK','SELL','WITH', 'THAT',
	'CALL','HAVE', 'NEXT','LINE','HAND','BOYS','MOST','FROM','APES','POLL','MORE',
	'SHORT','GOING','LEAPS','STILL','COVID','TRUMP','MOASS','GONNA','NOKIA','BEING','ABOUT',
	'CLASS','PRICE','STOCK','POWER',
	''}

	if len(word) > 5:  # ticker symbols will not be longer than 5 letters
		return False
	if word in BLACKLISTED_WORDS:
		return False	
	if all(letter.isupper() for letter in word):  # all letters must be uppercase
		return True




'''

Argparse Functions

UPPER_CASE_NAMES are local variables specific to each argparse function



'''


if args['scrape_all']:
	args['topstonks_trending_stocks_scraper'] = True
	args['thelion_wall_street_pit_scraper'] = True
	args['stockaholics_forum_scraper'] = True
	args['reddit_title_ticker_scraper'] = ['100', 'month', 'shortsqueeze', 'wallstreetbets', 'smallstreetbets', 'options', 'stocks', 'stock_picks', 'stockmarket']
	args['value_forum_scraper'] = ['200']


if args['topstonks_trending_stocks_scraper']:
	response = requests.get('https://topstonks.com/')
	tree = lxml.html.fromstring(response.content)
	# elements = [x for x in tree.xpath('//table[@class="t-home-table"]')]
	# elements = [x for x in tree.xpath('//tr[@className="table-light-row-cp-h"]')]
	elements = [x for x in tree.xpath('//div[@class="sparkline"]')]
	symbols = []
	for div in elements:
		byte = etree.tostring(div, pretty_print=True)
		word = byte.decode("utf-8") 
		word = word.split('sparkline')[-1]
		word = word.split('"')[0]
		symbols.append(word)

	print(f'\n----- TopStonks Trending Stocks\n{(symbols)}')




if args['stockaholics_forum_scraper']:
	response = requests.get('https://stockaholics.net/forums/stock-message-boards-nyse-nasdaq-amex.3/')
	tree = lxml.html.fromstring(response.content)
	elements = [x for x in tree.xpath('//div[@class="titleText"]')]
	symbols = []
	for div in elements:
		byte = etree.tostring(div, pretty_print=True)
		word = byte.decode("utf-8")
		index = word.find('data-previewurl')
		word = word[index:]
		index = word.find('>')
		word = word[index+1:]
		word = word[:5]
		stop_index = word.find(' ')
		word = word[:stop_index]
		if checkIfWordIsTicker(word):
			symbols.append(word)

	print(f'\n----- Stockaholics Front Page\n{(symbols)}')





if args['thelion_wall_street_pit_scraper']:
	response = requests.get('https://www.thelion.com/bin/forum.cgi?tf=wall_street_pit')
	df_list = pd.read_html(response.content)
	symbols = df_list[7][1]
	tickers = {}
	for w in symbols:
		if checkIfWordIsTicker(w):
			if w in tickers:
				tickers[w] += 1
			else:
				tickers[w] = 1

	sorted_tickers = sorted(tickers.items(), key=lambda item: item[1], reverse=True)
	print(f'\n----- The Lions Wall Street Pit\n{(sorted_tickers)}')






if args['value_forum_scraper']:
	NUMBER_OF_POSTS_TO_SCAN = int(args['value_forum_scraper'][0])
	response = requests.get('https://www.valueforum.com/forums/search.mpl?start=15&keywords=&fl=&so=&bustignore=&np='+str(NUMBER_OF_POSTS_TO_SCAN))
	tree = lxml.html.fromstring(response.content)
	df_list = pd.read_html(response.content)
	tickers = {}

	for i in range(0,NUMBER_OF_POSTS_TO_SCAN):
		# print(df_list[13][1][i])
		words = df_list[13][1][i].split(' ')

		for w in words:
			if checkIfWordIsTicker(w):
				if w in tickers:
					tickers[w] += 1
				else:
					tickers[w] = 1

	# Remove tickers with a count of one
	for k,v in list(tickers.items()):  # copy to list before iterating
		if v == 1:
			del tickers[k]		

	sorted_tickers = sorted(tickers.items(), key=lambda item: item[1], reverse=True)
	print(f'\n----- Value Forum Newest {NUMBER_OF_POSTS_TO_SCAN}\n{(sorted_tickers)}')






if args['reddit_title_ticker_scraper']:
	NUMBER_OF_POSTS_TO_SCAN = int(args['reddit_title_ticker_scraper'][0])
	DURATION = args['reddit_title_ticker_scraper'][1]
	HOT_TICKER_COUNT = {}
	TOP_TICKER_COUNT = {}


	def scanSubRedditPostTitlesForTickers(sub, number_of_posts_to_scan, duration=None):
		current_subreddit = reddit.subreddit(sub)
		tickers = {}
		words = []

		# Top
		if duration != None:
			for post in current_subreddit.top(duration, limit=number_of_posts_to_scan):
				for title_word in post.title.split(' '):
					words.append(title_word)

		# Hot
		if duration == None:
			for post in current_subreddit.hot(limit=NUMBER_OF_POSTS_TO_SCAN):
				for title_word in post.title.split(' '):
					words.append(title_word)

		# Find tickers
		for word in words:
			if word[0] == '$':  # drop any prepending dollar signs
				word = word[1:]
			if checkIfWordIsTicker(word):
				if word in tickers:
					tickers[word] += 1
				else:
					tickers[word] = 1

		# Remove tickers with a count of one
		for k,v in list(tickers.items()):  # copy to list before iterating
			if v == 1:
				del tickers[k]			

		# sort tickers by count and return
		return sorted(tickers.items(), key=lambda item: item[1], reverse=True)


	# Create API session
	reddit = praw.Reddit(client_id=config.cid, client_secret=config.secret, user_agent=config.agent)

	# loop through all subreddits
	for index, sub in enumerate(args['reddit_title_ticker_scraper']):

		if index == 0 or index == 1:
			continue

		TOP_TICKER_COUNT[sub] = scanSubRedditPostTitlesForTickers(sub, NUMBER_OF_POSTS_TO_SCAN, DURATION)
		HOT_TICKER_COUNT[sub] = scanSubRedditPostTitlesForTickers(sub, NUMBER_OF_POSTS_TO_SCAN)

	topdf = convertDictToPandasDataFrame(TOP_TICKER_COUNT)
	print(f'\n----- Reddit TOP {NUMBER_OF_POSTS_TO_SCAN} this {DURATION}\n{topdf}')

	hotdf = convertDictToPandasDataFrame(HOT_TICKER_COUNT)
	print(f'\n----- Reddit HOT {NUMBER_OF_POSTS_TO_SCAN}\n{hotdf}')












# End timing of script response time
toc = time.time()
print(f'\nElapsed time is {round((toc - tic), 2)} seconds')