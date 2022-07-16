import pandas as pd

df = pd.read_csv('finviz-nasdaq-07-2022.tsv', sep='\t')


df = df[df['Market Cap'] != '-']


dfSorted = df.sort_values(by=['Market Cap'], ascending=False)

print(dfSorted.head(10))
