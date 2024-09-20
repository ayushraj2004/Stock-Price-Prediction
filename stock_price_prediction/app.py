from flask import Flask, request, render_template, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

@app.route('/get_stock_data', methods=['GET'])
def get_stock_data():
    ticker = request.args.get('ticker')
    stock_data = fetch_stock_data(ticker)
    
    if stock_data is None or stock_data.empty:
        return jsonify({"error": "Could not fetch stock data or invalid ticker."})

    # Get the most recent row of data
    latest_data = stock_data.iloc[-1]
    
    return jsonify({
        "Open": latest_data['Open'],
        "High": latest_data['High'],
        "Low": latest_data['Low'],
        "Volume": latest_data['Volume']
    })

def fetch_stock_data(ticker):
    try:
        stock_data = yf.download(ticker, start='2023-01-01', end='2024-12-31')
        if stock_data.empty:
            return None
        return stock_data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

# Train a simple model based on historical data
def train_model(stock_data):
    stock_data = stock_data.dropna()  # Drop rows with missing values
    X = stock_data[['Open', 'High', 'Low', 'Volume']]
    y = stock_data['Close']

    model = LinearRegression()
    model.fit(X, y)
    return model

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for the prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get data from the form
    ticker = request.form['Ticker']
    open_price = float(request.form['Open'])
    high_price = float(request.form['High'])
    low_price = float(request.form['Low'])
    volume = float(request.form['Volume'])

    # Fetch stock data and train the model
    stock_data = fetch_stock_data(ticker)
    if stock_data is None:
        return render_template('result.html', prediction="Error: Could not fetch stock data.")

    model = train_model(stock_data)

    # Prepare data for prediction
    input_data = np.array([[open_price, high_price, low_price, volume]])
    prediction = model.predict(input_data)

    # Limit the prediction to two decimal places
    formatted_prediction = "{:.2f}".format(prediction[0])

    # Render the result
    return render_template('result.html', prediction=formatted_prediction)

if __name__ == '__main__':
    app.run(debug=True)
