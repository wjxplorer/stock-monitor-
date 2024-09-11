import yfinance as yf
import pandas as pd
import time

import requests
import numpy as np

API_KEY = 'cgronchr01qs9ra2097gcgronchr01qs9ra20980'
def get_realtime_data(ticker):
    url = f'https://finnhub.io/api/v1/quote?symbol={ticker}&token={API_KEY}'
    response = requests.get(url)
    data = response.json()
    # 将实时数据转换为 Pandas DataFrame 格式
    realtime_data = pd.DataFrame(
        {
            "Open": [data["o"]],
            "High": [data["h"]],
            "Low": [data["l"]],
            "Close": [data["c"]],
            "Volume": [np.nan],  # 将成交量设为 NaN
        },
        index=pd.to_datetime([pd.Timestamp.now()]),
    )

    return realtime_data

def get_stock_data(ticker, source):
    stock_data = get_yfinance_stock_data(ticker)
    return stock_data

def get_yfinance_stock_data(ticker):
    stock = yf.Ticker(ticker)
    stock_data = stock.history(period='1d', interval='1m')
    stock_data.reset_index(inplace=True)
    return stock_data

def format_stock_data(stock_data):
    formatted_stock_data = stock_data.copy()
    formatted_stock_data['Datetime'] = pd.to_datetime(formatted_stock_data['Datetime'])
    formatted_stock_data = formatted_stock_data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return formatted_stock_data

def get_multiple_stocks_data(stock_list):
    multiple_stocks_data = {}
    
    for stock in stock_list:
        ticker, market = stock['ticker'], stock['market']
        stock_data = get_stock_data(ticker, market)
        formatted_stock_data = format_stock_data(stock_data)
        # 获取实时数据
        realtime_data = get_realtime_data(ticker)

        # 将实时数据和历史数据结合
        combined_data = pd.concat([formatted_stock_data, realtime_data]).reset_index(drop=True)

        multiple_stocks_data[ticker] = combined_data
    
    return multiple_stocks_data
print(get_realtime_data('AAPL'))