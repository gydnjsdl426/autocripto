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
        if d > 1.095:
            data.append(d)
            TICKERS.append(ticker)

        time.sleep(0.1)

update()
schedule.every(1).hours.do(update)

mean20 = 0
ma5= 0
def get_ma(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=25)
    sum=0
    for i in np.arange(0,20):
        sum+=df['close'][i:5+i].rolling(5).mean().iloc[-1]  

    mean20=sum/20
    ma5=df['close'].rolling(5).mean().iloc[-1]

    print(ticker)
    print(mean20)
    print(ma5)

    return mean20 < ma5 < mean20*1.01

while True:
    schedule.run_pending()
    try:
        all = pyupbit.get_current_price(TICKERS)
        total = get_total()
        

        for ticker in TICKERS:
            krw = upbit.get_balance("KRW")
            if get_ma(ticker) and all[ticker] > mean20 and upbit.get_balance(ticker) == 0:
                if krw > 5000:
                    upbit.buy_market_order(ticker, total*0.245)

            elif upbit.get_balance(ticker) != 0 and not(upbit.get_avg_buy_price(ticker) * 0.995 < all[ticker] < upbit.get_avg_buy_price(ticker) * 1.007):
                upbit.sell_market_order(ticker, upbit.get_balance(ticker))
            time.sleep(0.08)
            
    except Exception as e:
        print(e)
        time.sleep(0.5)
