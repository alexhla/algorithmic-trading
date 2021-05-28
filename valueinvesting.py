

# Depressed Industries

# Enterprise Value (Cost to Purchase Business)

# EV = Market Capitalization + Total Debt - Cash

# Extended EV = Common Shares + Preferred Shares + Market Value of Debt + Minority Interest – Cash and Equivalents


# Earnings before Interest, Taxes, Depreciations, Ammoratizations

# EBITDA = 

# EV / EBITDA (Cost of Business over Earnings)

from bs4 import BeautifulSoup as bs

filepath = 'sec-edgar-filings/CASI/10-Q/0001558370-21-007013/filing-details.html'

with open(filepath) as fp:
    soup = bs(fp, 'html.parser')




tablerow = soup.select('tr:-soup-contains("Cash and cash equivalents")')
tabledata = tablerow[0].select('td:-soup-contains(",", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9")')

tablerow = soup.select('tr:-soup-contains("Total current liabilities")')
tabledata = tablerow[0].select('td:-soup-contains(",", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9")')



for i, t in enumerate(tabledata):
	# print(f'{dir(t)}\n')
	print(f'{int(t.text.strip().replace(",",""))}\n')
	print(f'-----------{i}/{type(t)}')