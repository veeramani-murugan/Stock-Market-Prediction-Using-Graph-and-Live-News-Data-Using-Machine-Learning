import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import seaborn as sns
import datetime as dt
import time
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense
from sklearn.model_selection import train_test_split

def data(ticker):
    # Get the current date
    x = str(dt.datetime.now())[0:10].split("-")
    print(x)
    start = dt.datetime(int(x[0])-1, int(x[1]), int(x[-1]))
    end = dt.datetime(int(x[0]), int(x[1]), int(x[-1]))
    print(start, end)

    # Download stock data using yfinance
    try:
        df = yf.download(ticker, start=start, end=end)
        print(f"Data for {ticker} fetched successfully.")
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return

    # Extract 'Close' prices
    data = df[['Close']]
    df.to_csv(ticker + ".csv")

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data)

    # Function to create sequences for the GRU model
    def create_sequences(data, time_steps):
        x, y = [], []
        for i in range(len(data) - time_steps):
            x.append(data[i:(i + time_steps), 0])
            y.append(data[i + time_steps, 0])
        return np.array(x), np.array(y)

    # Define the time steps and create sequences
    time_steps = 10  # Adjust as needed
    x, y = create_sequences(data_scaled, time_steps)

    # Split the data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Reshape the data for input to GRU
    x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 1)
    x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], 1)

    # Build the GRU model
    model = Sequential()
    model.add(GRU(units=50, activation='relu', input_shape=(x_train.shape[1], 1)))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(x_train, y_train, epochs=50, batch_size=32)

    # Use the last 'time_steps' data points to predict the next values
    future_sequence = data_scaled[-time_steps:].reshape(1, time_steps, 1)

    # Number of future values to predict
    num_predictions = 10  # Adjust as needed
    future_predictions = []

    for _ in range(num_predictions):
        next_prediction = model.predict(future_sequence)
        future_predictions.append(next_prediction[0, 0])
        future_sequence = np.append(future_sequence[:, 1:, :], np.array([[next_prediction[0, 0]]]).reshape(1, 1, 1), axis=1)

    # Inverse transform the future predictions
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    # Display the future predictions
    print("Future Predictions:")
    print(future_predictions.flatten())

    # Plot the actual and predicted future values
    plt.figure(figsize=(12, 6))

    # Plot the actual closing prices
    plt.plot(data.index, scaler.inverse_transform(data_scaled), label='Actual Close Prices')

    # Create a new time index for the future predictions
    future_index = pd.date_range(df.index[-1], periods=num_predictions + 1, freq='B')[1:]

    # Plot the future predictions
    plt.plot(future_index, future_predictions, label='Future Predictions', linestyle='dashed')

    # Customize the plot
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.title(f'{ticker} - Actual vs Predicted Close Prices')
    plt.legend()

    # Save the plot to a file
    plt.savefig(ticker + ".png")
    print("Prediction plot saved.")

# Call the function with the desired ticker
data("MSUMI.NS")
