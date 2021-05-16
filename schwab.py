import argparse
import time
import csv

# Begin timing of script response time
tic = time.time()

# Instantiate the argument parser object
ap = argparse.ArgumentParser()

# Add the arguments to the parser

ap.add_argument('-rcsv', '--readcsv',  action='store_true')


# Parse user arguments
args = vars(ap.parse_args())
# print(f'\nargs --- {args}\n')


if args['readcsv']:
	tickers = []
	with open('schwab.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for index, row in enumerate(csv_reader):
			if index == 0:
				pass
			else:
				tickers.append(row[0])
	print(tickers)

# End timing of script response time
toc = time.time()
print(f'\nElapsed time is {round((toc - tic), 2)} seconds')