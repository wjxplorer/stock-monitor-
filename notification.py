import yagmail

def send_email(subject, body, recipient):
    # 请替换为你的网易邮箱地址和授权码
    email_address = 'quantwjx@163.com'
    email_password = 'BYKLRXQWGUHAPZBH'
    
    yag = yagmail.SMTP(user=email_address, password=email_password, host='smtp.163.com', port=465)
    print(subject)
    print(body)
    yag.send(to=recipient, subject=subject, contents=body)

def format_email_content(stock_info, account_info):
    email_content = ""
    for stock in stock_info:
        signal_type = '买入' if stock['trade_strategy'] == 'buy' else '卖出'
        email_content += f"信号: {signal_type}\n"
        email_content += f"股票代码: {stock['ticker']}\n"
        email_content += f"价格区间: {stock['price_range']}\n"
        email_content += f"股数: {stock['shares']}\n\n"
    
    email_content += f"账户余额:\n"
    email_content += f"美元: {account_info['usd_balance']} 美元\n"
    
    return email_content
