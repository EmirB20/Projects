
import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    stock_data.reset_index(inplace=True)
    return stock_data

def add_features(data, window=10):
    data['SMA'] = data['Adj Close'].rolling(window).mean()
    data['RSI'] = compute_rsi(data['Adj Close'], window)
    data['Upper Band'], data['Lower Band'] = compute_bollinger_bands(data['Adj Close'], window)
    return data

def compute_rsi(prices, window=14):
    delta = prices.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=window).mean()
    avg_loss = pd.Series(loss).rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_bollinger_bands(prices, window=20):
    sma = prices.rolling(window).mean()
    std_dev = prices.rolling(window).std()
    upper_band = sma + (2 * std_dev)
    lower_band = sma - (2 * std_dev)
    return upper_band, lower_band

def evaluate_model(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    return rmse, mae

def predict_prices(data, x):
    dates = pd.to_datetime(data['Date']).dt.to_pydatetime()
    prices = data['Adj Close'].values
    dates_numeric = np.array([date.timestamp() for date in dates]).reshape(-1, 1)

    # Features
    sma_prices = data['SMA'].fillna(0).values

    # SVR model
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_rbf.fit(dates_numeric, prices)

    # Linear model
    linear_model = LinearRegression()
    linear_model.fit(dates_numeric, prices)

    # Polynomial model
    degree = 2
    poly_features = PolynomialFeatures(degree=degree)
    dates_poly = poly_features.fit_transform(dates_numeric)
    poly_model = LinearRegression()
    poly_model.fit(dates_poly, prices)

    # Random Forest model
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(dates_numeric, prices)

    # XGBoost model
    xgb_model = XGBRegressor(n_estimators=100, random_state=42)
    xgb_model.fit(dates_numeric, prices)

    # ARIMA model
    arima_model = ARIMA(prices, order=(5, 1, 0))
    arima_fit = arima_model.fit()

    # Predictions for visualization
    dates_pred = [dates[-1] + timedelta(days=i) for i in range(1, 11)]
    dates_pred_numeric = np.array([date.timestamp() for date in dates_pred]).reshape(-1, 1)
    predictions = {
        "SVR": svr_rbf.predict(dates_pred_numeric),
        "Linear": linear_model.predict(dates_pred_numeric),
        "Polynomial": poly_model.predict(poly_features.transform(dates_pred_numeric)),
        "Random Forest": rf_model.predict(dates_pred_numeric),
        "XGBoost": xgb_model.predict(dates_pred_numeric),
        "ARIMA": arima_fit.forecast(steps=10)
    }

    # Model Evaluation
    metrics = {}
    for model, pred in predictions.items():
        rmse, mae = evaluate_model(prices[-10:], pred[:10])
        metrics[model] = {"RMSE": rmse, "MAE": mae}

    return predictions, dates_pred, metrics

def visualize_predictions(data, predictions, dates_pred, metrics):
    fig = make_subplots(rows=2, cols=1, subplot_titles=("Candlestick Chart with Predictions", "Model Predictions"))

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Adj Close'],
            name="Candlestick"
        ),
        row=1, col=1
    )

    # Model Predictions
    for model, pred in predictions.items():
        fig.add_trace(
            go.Scatter(
                x=dates_pred,
                y=pred,
                mode='lines+markers',
                name=f"{model} Predictions"
            ),
            row=2, col=1
        )

    fig.update_layout(
        title="Stock Price Prediction",
        xaxis_title="Date",
        yaxis_title="Price",
        height=800,
        showlegend=True
    )

    fig.show()

    # Display metrics as a table
    metrics_df = pd.DataFrame(metrics).T
    print("\nModel Evaluation Metrics:")
    print(metrics_df)


symbol = 'DOGE-USD'  # Sample Ticker
start_date = '2024-01-01'
end_date = '2024-03-03'

data = get_data(symbol, start_date, end_date)
data = add_features(data)

predictions, dates_pred, metrics = predict_prices(data, '03/04/2024')

visualize_predictions(data, predictions, dates_pred, metrics)

