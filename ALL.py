import time
import pyupbit
import datetime
import numpy as np
import schedule

access = "KHTqX6NbkdKaY7saJo40FCjRF8zhLvB2WkADnajD"
secret = "vIIe18R6kquGERglLWfKSC5UxKxfQA6DP4rq2UWc"

upbit = pyupbit.Upbit(access, secret)
tickers = pyupbit.get_tickers(fiat="KRW")
print("autotrade start")

def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_total():
    balances = upbit.get_balances()
    total = float(balances[0]['balance'])
    for balance in balances:
        total = float(total) + float(balance['balance']) * float(balance['avg_buy_price'])
    return total

data=[]
TICKERS=[]
def update():
    for ticker in TICKERS:
            if upbit.get_balance(ticker) != 0:
                upbit.sell_market_order(ticker, upbit.get_balance(ticker))

    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, interval = "day", count=3)
        df['range'] = df['high'] / df['low']
        d = df['range'].rolling(3).mean().iloc[-1]
        if d > 1.11:
            data.append(d)
            TICKERS.append(ticker)

        time.sleep(0.1)

update()
schedule.every(6).hours.do(update)

mean20 = 0
ma5= 0
def get_ma(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
    ma5=df['close'].rolling(3).mean().iloc[-1]
    ma20=df['close'].rolling(20).mean().iloc[-1]

    inclination = ma5 - df['close'][0:5].rolling(5).mean().iloc[-1]
    
    # print(ticker)
    # print(mean20)
    # print(ma5)

    if inclination > 0 and ma5 >= ma20 * 0.995:
        return 1 # Buy

    if inclination < 0 and ma5 <= ma20 * 1.005:
        return 0 # Sell

    else:
        return -1 # Nothing

while True:
    schedule.run_pending()
    try:
        all = pyupbit.get_current_price(TICKERS)
        total = get_total()

        for ticker in TICKERS:
            krw = upbit.get_balance("KRW")
            bal = upbit.get_balance(ticker)
            swch = get_ma(ticker)
            
            if swch == 1:
                if krw > 5000 and bal == 0:
                    upbit.buy_market_order(ticker, total*0.197)

            elif bal != 0 and swch == 0: 
                upbit.sell_market_order(ticker, bal)
            
    except Exception as e:
        print(e)
        time.sleep(0.5)
