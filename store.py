from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np

import requests
import pandas as pd
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
topic="stock"
site = 'https://news.google.com/rss/search?q={}'.format(topic)
op = urlopen(site)  # Open that site
rd = op.read()  # read data from site
op.close()  # close the object
sp_page = soup(rd, 'xml')  # scrapping data from site
news_title = sp_page.find_all("title")  # finding news
news_pubDate = sp_page.find_all("pubDate")  # finding news
headlines={"title":[],"publishdate":[]}
for k in range(100):
    try:

        headlines["publishdate"].append(news_pubDate[k].get_text())
        headlines["title"].append(news_title[k].get_text())
    except :
        pass
print(len(headlines["title"]),len(headlines["publishdate"]))
df = pd.DataFrame(headlines)
df.to_csv("news.csv")
analyser = SentimentIntensityAnalyzer()
headlines= pd.read_csv("news.csv")

i=0 #counter
compval1 = [ ]  #empty list to hold our computed 'compound' VADER scores
while i<len(headlines):
    k = analyser.polarity_scores(headlines.iloc[i]['title'])
    compval1.append(k['compound'])
    i = i+1
compval1 = np.array(compval1)
len(compval1)

headlines['VADER score'] = compval1
i = 0
predicted_value = [ ] #empty series to hold our predicted values
while(i<len(headlines)):
    if ((headlines.iloc[i]['VADER score'] >= 0.1)):
        predicted_value.append('positive')
        i = i+1
    elif ((headlines.iloc[i]['VADER score'] > -0.1) & (headlines.iloc[i]['VADER score'] < 0.1)):
        predicted_value.append('neutral')
        i = i+1
    elif ((headlines.iloc[i]['VADER score'] <= -0.1)):
        predicted_value.append('negative')
        i = i+1
headlines['sentiment'] = predicted_value
headlines.to_csv("processednew.csv")
