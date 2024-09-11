import get_data
import signal_generation
import capital_management
import notification
import time

import datetime
import pytz


def is_market_open(market):
    local_timezone = pytz.timezone('America/New_York')
    local_time = datetime.datetime.now(local_timezone)

    # 检查是否为工作日（周一至周五）
    if local_time.weekday() >= 5:
        return False

    # 检查是否在交易时间内
    market_open_time = local_time.replace(hour=9, minute=30, second=0)
    market_close_time = local_time.replace(hour=16, minute=0, second=0)

    return market_open_time <= local_time <= market_close_time


def get_next_open_time():
    timezone = pytz.timezone('America/New_York')
    open_hour, open_minute = 9, 30

    now = datetime.datetime.now(timezone)
    next_open_time = now.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
    if now >= next_open_time:
        next_open_time += datetime.timedelta(days=1)
    while next_open_time.weekday() > 4:  # Skip weekends
        next_open_time += datetime.timedelta(days=1)
    return next_open_time.strftime("%Y-%m-%d %H:%M:%S")


def main():
    # 初始化账户
    account = capital_management.initialize_account(500, 5000)

    # 设置股票观察列表
    stock_list = [
        {'ticker': 'AAPL', 'market': 'us'},
        {'ticker': 'TSLA', 'market': 'us'},
        {'ticker': 'BABA', 'market': 'us'},
        {'ticker': 'NVDA', 'market': 'us'}
    ]

    # 设置循环，每分钟执行一次
    while True:

        # 检查美股市场是否开放
        market_open = is_market_open('us')
        local_time = datetime.datetime.now(pytz.timezone('America/New_York'))
        print(f'现在美股时间：{local_time.strftime("%Y-%m-%d %H:%M:%S")}, 美股市场：{"开放" if market_open else "关闭"}')

        if market_open:
            print("美股市场开放，正在盯盘...")
            # 获取美股数据并执行相关操作...
            stock_data = get_data.get_multiple_stocks_data(stock_list)

            # 生成买入和卖出信号
            account = signal_generation.apply_signal_strategy(stock_data, account)
            print(account)
        else:
            next_open_time = get_next_open_time()
            print(f"美股市场已关闭，等待下一个交易时间段。")
            print(f"下次美股开盘时间：{next_open_time}")

        # 暂停1分钟
        time.sleep(60)


if __name__ == '__main__':
    main()
