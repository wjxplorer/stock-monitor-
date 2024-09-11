import capital_management as cm
from capital_management import process_buy_order, process_sell_order

import get_data as gd
import numpy as np
import time
import notification
import pandas as pd


# 计算买入和卖出的价格区间
def calculate_buy_sell_ranges(stock_data, buy_threshold, sell_threshold):
    close_price = stock_data['Close']
    buy_range = (close_price[0] * (1 - buy_threshold), close_price[0] * (1 + buy_threshold))
    sell_range = (close_price[0] * (1 - sell_threshold), close_price[0] * (1 + sell_threshold))
    return buy_range, sell_range

# 根据可用资金、股票数据、股票类型和最大投资百分比计算买入的股数
def determine_order_size(account, ticker, order_type, price_range, max_percentage = 0.5):
    stock_type = 'HKD' if '.HK' in ticker else 'USD'
    available_capital = account[stock_type]['cash']
    min_price, max_price = price_range
    avg_price = (min_price + max_price) / 2

    if order_type == 'buy':
        max_investment = available_capital * max_percentage
        max_affordable_shares = int(max_investment / avg_price)
        return max_affordable_shares

    elif order_type == 'sell':
        if ticker in account[stock_type]['stocks']:
            return account[stock_type]['stocks'][ticker]['shares']
        else:
            return 0
    else:
        raise ValueError(f"Invalid order_type: {order_type}")

# 根据买入价格、卖出价格、股数和交易成本计算交易收益
def calculate_profit(buy_price, sell_price, order_size, trade_costs):
    gross_profit = (sell_price - buy_price) * order_size
    net_profit = gross_profit - trade_costs['buy_cost'] - trade_costs['sell_cost']
    return net_profit

# 更新账户余额，包括买入卖出操作后的现金和股票价值
def update_account_balance(account, ticker, order_type, order_size, price_range, trade_costs):
    if order_type == 'buy':
        cost = price_range[1] * order_size + trade_costs['buy_cost']
        account['cash'][account['currency']] -= cost
        account['stocks'][ticker] = {'shares': order_size, 'buy_price': price_range[1]}
    elif order_type == 'sell':
        revenue = price_range[0] * order_size - trade_costs['sell_cost']
        account['cash'][account['currency']] += revenue
        del account['stocks'][ticker]

    return account

# 这里我们使用简单的移动平均线策略作为示例。
# 当股票的当前价格高于其短期移动平均线并且短期移动平均线高于长期移动平均线时，我们认为这是一个买入信号；
# 当股票的当前价格低于其短期移动平均线并且短期移动平均线低于长期移动平均线时，我们认为这是一个卖出信号。
def moving_average(data, window):
    return np.convolve(data, np.ones(window), 'valid') / window

last_signal_time = None
last_signal_type = None
def get_signal(stock_data, short_window=5, long_window=20, signal_interval=5):
    global last_signal_time
    global last_signal_type
    # 根据股票数据和交易策略生成买卖信号
    signals = []
    for ticker, data in stock_data.items():
        # 计算短期和长期移动平均线
        short_ma = moving_average(data['Close'], short_window)
        long_ma = moving_average(data['Close'], long_window)

        # 初始化信号列表
        signal = {'ticker': ticker, 'buy': [], 'sell': []}

        # 遍历数据，生成买卖信号
        for i in range(long_window - 1, len(data['Close'])):
            current_price = data['Close'][i]
            short_ma_price = short_ma[i - short_window + 1] if i >= short_window else np.nan
            long_ma_price = long_ma[i - long_window + 1]

            if not np.isnan(short_ma_price):

              ma_diff = short_ma_price - long_ma_price

              if ma_diff > 0:  # 买入信号
                  signal_strength = ma_diff
                  signal['buy'].append((signal_strength, i))

              elif ma_diff < 0:  # 卖出信号
                  signal_strength = -ma_diff
                  signal['sell'].append((signal_strength, i))

        signals.append(signal)
    trade_info = get_trade_info(signals)
    print("trade_info=", trade_info)
    return signals

def get_trade_info(signals):
    trade_info = []

    for signal in signals:
        ticker = signal['ticker']
        total_buy_strength = sum([x[0] for x in signal['buy']])
        total_sell_strength = sum([x[0] for x in signal['sell']])

        if total_buy_strength > total_sell_strength:
            trade_strategy = 'buy'
        else:
            trade_strategy = 'sell'

        trade_info.append({'ticker': ticker, 'trade_strategy': trade_strategy})

    return trade_info

def apply_signal_strategy(stock_data, account, buy_threshold=0.02, sell_threshold=0.02):
    signals = get_signal(stock_data)
    trade_info = get_trade_info(signals)
    stock_info = []
    for trade in trade_info:
        ticker = trade['ticker']
        stock_type = 'HKD' if '.HK' in ticker else 'USD'
        if trade['trade_strategy'] == 'buy':
          buy_range, sell_range = calculate_buy_sell_ranges(stock_data[ticker], buy_threshold, sell_threshold)
          order_size = determine_order_size(account, ticker, 'buy', buy_range)
          if order_size > 0:
              stock_info.append({
                  'ticker': ticker,
                  'trade_strategy': 'buy',
                  'price_range': buy_range,
                  'shares': order_size
              })
              price = (buy_range[0] + buy_range[1]) / 2
              process_buy_order(account, ticker, order_size, price, stock_type)
        if trade['trade_strategy'] == 'sell':
            buy_range, sell_range = calculate_buy_sell_ranges(stock_data[ticker], buy_threshold, sell_threshold)
            order_size = determine_order_size(account, ticker, 'sell', sell_range)
            if order_size > 0:
                stock_info.append({
                    'ticker': ticker,
                    'trade_strategy': 'sell',
                    'price_range': sell_range,
                    'shares': order_size
                })
                price = (buy_range[0] + buy_range[1]) / 2
                process_buy_order(account, ticker, order_size, price, stock_type)

    if (len(stock_info)):
        account_info = {'hkd_balance': account['HKD']['cash'], 'usd_balance': account['USD']['cash']}

        email_body = notification.format_email_content(stock_info, account_info)

        email_subject = f"Trading signal for {stock_info[0]['ticker']}"
        notification.send_email(email_subject, email_body, 'quantwjx@163.com')

    return account
