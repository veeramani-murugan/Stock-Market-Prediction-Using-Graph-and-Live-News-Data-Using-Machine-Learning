import time
import datetime as dt
import pandas as pd

ticker = 'AAPL'
x = str(dt.datetime.now())[0:10].split("-")
print(x)
start = dt.datetime(int(x[0])-1, int(x[1]), int(x[-1]))
end = dt.datetime(int(x[0]), int(x[1]), int(x[-1]))
print(start,end)

period1 = int(time.mktime(dt.datetime(int(x[0])-1, int(x[1]), int(x[2]), 23, 59).timetuple()))
period2 = int(time.mktime(dt.datetime(int(x[0]), int(x[1]), int(x[2]), 23, 59).timetuple()))
print(period1,period2)
interval = '1d' # 1d, 1m

query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'

df = pd.read_csv(query_string)
# print(df)
df.to_csv('AAPL.csv')
