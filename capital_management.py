def initialize_account(initial_usd, initial_hkd):
    account = {
        'USD': {
            'cash': initial_usd,
            'stocks': {}
        },
        'HKD': {
            'cash': initial_hkd,
            'stocks': {}
        }
    }
    return account

# 计算账户中股票和现金的总价值
def calculate_account_value(account, stock_prices):
    total_value = {'USD': 0, 'HKD': 0}

    for currency in account:
        total_value[currency] += account[currency]['cash']

        for ticker, shares in account[currency]['stocks'].items():
            stock_price = stock_prices[ticker]
            total_value[currency] += stock_price * shares

    return total_value

# 计算可用于交易的资金。
def calculate_available_capital(account, stock_prices):
    account_value = calculate_account_value(account, stock_prices)
    available_capital = {'USD': 0, 'HKD': 0}

    for currency in account_value:
        available_capital[currency] = account_value[currency] * 0.3

    return available_capital

# 获取货币汇率
def get_currency_conversion_rate():
    # 你可以从外部 API 获取汇率，或者使用固定值。这里我们使用一个固定值。
    usd_to_hkd = 7.8
    return usd_to_hkd

# 根据给定的汇率转换货币
def convert_currency(amount, conversion_rate, reverse=False):
    if reverse:
        return amount / conversion_rate
    else:
        return amount * conversion_rate

# 计算交易成本（包括手续费）     
def calculate_trade_costs(currency):
    if currency == 'USD':
        return 2
    else:
        return 50

# 处理买入订单，更新账户余额和持仓
def process_buy_order(account, ticker, shares, close_price, currency):
    avg_price = close_price
    total_cost = avg_price * shares + calculate_trade_costs(currency)

    if account[currency]['cash'] >= total_cost:
        account[currency]['cash'] -= total_cost
        if ticker not in account[currency]['stocks']:
            account[currency]['stocks'][ticker] = {'shares': shares, 'avg_price': avg_price}
        else:
            current_shares = account[currency]['stocks'][ticker]['shares']
            current_avg_price = account[currency]['stocks'][ticker]['avg_price']
            new_avg_price = ((current_avg_price * current_shares) + (avg_price * shares)) / (current_shares + shares)

            account[currency]['stocks'][ticker]['shares'] += shares
            account[currency]['stocks'][ticker]['avg_price'] = new_avg_price
    else:
        print(f"Insufficient balance to buy {shares} shares of {ticker}.")

# 处理卖出订单，更新账户余额和持仓
def process_sell_order(account, ticker, shares, close_price, currency):
    avg_price = close_price
    total_value = avg_price * shares

    if ticker in account[currency]['stocks'] and account[currency]['stocks'][ticker]['shares'] >= shares:
        account[currency]['stocks'][ticker]['shares'] -= shares
        account[currency]['cash'] += total_value

        if account[currency]['stocks'][ticker]['shares'] == 0:
            del account[currency]['stocks'][ticker]
    else:
        print(f"Insufficient shares to sell {shares} shares of {ticker}.")
