import argparse
import time
import csv


# Local imports
import config

# Begin timing of script response time
tic = time.time()

# Instantiate the argument parser object
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument('-sbox', '--sandbox', action='store_true',
	help='sandbox is for running prototype code and tests')

# ap.add_argument('-all', '--scrape_all',  action='store_true',
# 	help='Calls all scrapers i.e. -reddit -thelion -')

ap.add_argument('-readcsv', '--readcsv',  action='store_true',
	help='')


# Parse user arguments
args = vars(ap.parse_args())
# print(f'\nargs --- {args}\n')




'''

Utility Functions

camelCaseNames are local function names

UPPER_CASE_NAMES are local variables specific to each local function

'''




'''

Argparse Functions

UPPER_CASE_NAMES are local variables specific to each argparse function



'''


if args['sandbox']:
	print('------- Sandbox --------')
	for style in ALL_STYLES:
		sp_path = 'img/squarespace/product-images/'+style+'/self-portraits/'
		new_path = 'img/squarespace/product-images/'+style+'/portraits/'
		if(os.path.isdir(sp_path)):
			os.rename(sp_path, new_path)




# if args['scrape_all']:
# 	args['topstonks_trending_stocks_scraper'] = True
# 	args['thelion_wall_street_pit_scraper'] = True
# 	args['stockaholics_forum_scraper'] = True
# 	args['reddit_title_ticker_scraper'] = ['100', 'month', 'shortsqueeze', 'wallstreetbets', 'smallstreetbets', 'options', 'stocks', 'stock_picks', 'stockmarket']
# 	args['value_forum_scraper'] = ['200']


if args['readcsv']:
	tickers = {}
	with open('schwabstocks.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for index, row in enumerate(csv_reader):
			if index == 0:
				pass
			else:
				tickers.append(row[0])



# End timing of script response time
toc = time.time()
print(f'\nElapsed time is {round((toc - tic), 2)} seconds')