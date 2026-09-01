import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import seaborn as sns
import datetime as dt
import time
import yfinance as yf
import requests
from bs4 import BeautifulSoup as soup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense
from sklearn.model_selection import train_test_split
import nltk

# Download required nltk data
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')

def data(ticker):
    """Fetches stock data, trains a GRU model, and analyzes news sentiment."""
    
    # Get today's date
    today = dt.datetime.now().strftime('%Y-%m-%d')
    one_year_ago = (dt.datetime.now() - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"Fetching stock data for {ticker} from {one_year_ago} to {today}...")

    # Fetch stock data using yfinance
    stock = yf.download(ticker, start=one_year_ago, end=today, interval="1d")

    if stock.empty:
        print(f"Error: Could not fetch stock data for {ticker}")
        return

    stock.to_csv(f"{ticker}.csv")
    data = stock[['Close']]

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data)

    # Function to create sequences for GRU model
    def create_sequences(data, time_steps=10):
        x, y = [], []
        for i in range(len(data) - time_steps):
            x.append(data[i:(i + time_steps), 0])
            y.append(data[i + time_steps, 0])
        return np.array(x), np.array(y)

    # Create sequences
    time_steps = 10
    x, y = create_sequences(data_scaled, time_steps)

    # Split data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    
    # Reshape for GRU model
    x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 1)
    x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], 1)

    # Build GRU model
    model = Sequential([
        GRU(units=50, activation='relu', input_shape=(x_train.shape[1], 1)),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(x_train, y_train, epochs=50, batch_size=32, verbose=1)

    # Predict future values
    future_sequence = data_scaled[-time_steps:].reshape(1, time_steps, 1)
    num_predictions = 10
    future_predictions = []

    for _ in range(num_predictions):
        next_prediction = model.predict(future_sequence)
        future_predictions.append(next_prediction[0, 0])

        # FIX: Ensure correct dimensions
        future_sequence = np.append(future_sequence[:, 1:, :], [[[next_prediction[0, 0]]]], axis=1)

    # Inverse transform predictions
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    # Prepare dates for plotting
    actual_dates = stock.index  # Dates of actual stock data
    future_dates = pd.date_range(start=actual_dates[-1], periods=num_predictions + 1)[1:]

    # Plot actual and predicted prices
    plt.figure(figsize=(12, 6))
    
    # Plot actual stock prices
    plt.plot(actual_dates, scaler.inverse_transform(data_scaled), label='Actual Close Prices', color='blue')

    # Plot future predicted stock prices
    plt.plot(future_dates, future_predictions, label='Predicted Future Prices', linestyle='dashed', color='red', marker='o')

    # Enhancements
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title(f"Stock Price Prediction for {ticker}")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

    # Save and show plot
    plt.savefig(f"static/{ticker}.png")
    # plt.show()

    print("Stock price prediction completed. Now fetching news sentiment analysis...")

def newsdetails():
    # NEWS SCRAPING & SENTIMENT ANALYSIS
    topic = f"stock"
    site = f'https://news.google.com/rss/search?q={topic}'

    response = requests.get(site)
    if response.status_code != 200:
        print("Error fetching news data")
        return

    # Parse news feed
    sp_page = soup(response.text, 'xml')
    news_titles = sp_page.find_all("title")
    news_dates = sp_page.find_all("pubDate")

    # Ensure we do not exceed the length of the shorter list
    num_articles = min(len(news_titles), len(news_dates), 100)  # Limit to 100

    headlines = {"title": [], "publish_date": []}

    for k in range(num_articles):  # Loop only within available range
        headlines["title"].append(news_titles[k].get_text())
        headlines["publish_date"].append(news_dates[k].get_text())

    # Convert to DataFrame and save
    df_news = pd.DataFrame(headlines)
    df_news.to_csv("news.csv", index=False)

    # Sentiment Analysis
    analyser = SentimentIntensityAnalyzer()
    df_news["VADER score"] = df_news["title"].apply(lambda x: analyser.polarity_scores(x)['compound'])

    # Classify sentiment
    def classify_sentiment(score):
        if score >= 0.1:
            return 'positive'
        elif score <= -0.1:
            return 'negative'
        else:
            return 'neutral'

    df_news["sentiment"] = df_news["VADER score"].apply(classify_sentiment)
    df_news.to_csv("processed_news.csv", index=False)

    print("News sentiment analysis completed. Results saved in processed_news.csv.")

# Run the function
data("AMZN")
data("ADANIPOWER.NS")
data("GOOG")


