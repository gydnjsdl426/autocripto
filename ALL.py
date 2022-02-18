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
    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, interval = "day", count=3)
        df['range'] = df['high'] / df['low']
        d = df['range'].rolling(3).mean().iloc[-1]
        if d > 1.1:
            data.append(d)
            TICKERS.append(ticker)

        time.sleep(0.1)

update()
schedule.every(2).hours.do(update)

mean20 = 0
ma5= 0
def get_ma(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=25)
    sum=0
    for i in np.arange(0,20):
        sum+=df['close'][i:5+i].rolling(5).mean().iloc[-1]  

    mean20=sum/20
    ma5=df['close'].rolling(5).mean().iloc[-1]

    # print(ticker)
    # print(mean20)
    # print(ma5)

    return mean20 < ma5 < mean20*1.01

while True:
    schedule.run_pending()
    try:
        all = pyupbit.get_current_price(TICKERS)
        total = get_total()
        start_time = get_start_time("KRW-BTC") + datetime.timedelta(minutes=30)
        end_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(minutes=1)
        now = datetime.datetime.now()

        if start_time < now < end_time:
            for ticker in TICKERS:
                krw = upbit.get_balance("KRW")
                if get_ma(ticker):
                    if krw > 5000 and upbit.get_balance(ticker) == 0:
                        upbit.buy_market_order(ticker, total*0.197)

                elif upbit.get_balance(ticker) != 0 and (upbit.get_avg_buy_price(ticker) * 0.993 > all[ticker] or all[ticker] > upbit.get_avg_buy_price(ticker) * 1.002):
                    upbit.sell_market_order(ticker, upbit.get_balance(ticker))
                time.sleep(0.07)
        else:
            for ticker in TICKERS:
                if upbit.get_balance(ticker) != 0:
                    upbit.sell_market_order(ticker, upbit.get_balance(ticker))

            update()
            
    except Exception as e:
        print(e)
        time.sleep(0.5)
