import time
import pyupbit
import datetime
import numpy as np
import schedule

access = "KHTqX6NbkdKaY7saJo40FCjRF8zhLvB2WkADnajD"
secret = "vIIe18R6kquGERglLWfKSC5UxKxfQA6DP4rq2UWc"

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    time.sleep(0.07)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

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

def get_ror(ticker):
    df = pyupbit.get_ohlcv(ticker, interval = "day", count=7)
    ror=[]
    map={'ticker':'name','index':0,'value':0}
    for k in np.arange(0, 1.0, 0.1):
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        fee = 0.0032
        df['ror'] = np.where(df['high'] > df['target'],
                            df['close'] / df['target'] - fee,
                            1)

        ror.append(df['ror'].cumprod()[-2])

    map['ticker']=ticker
    map['index']=ror.index(max(ror)) / 10
    map['value']=max(ror)
    return map

def update_target():
    tickers = pyupbit.get_tickers(fiat="KRW")
    global target_prices
    global TICKERS
    target_prices = []
    TICKERS = []
    maps=[]
    for ticker in tickers:
        try:
            maps.append(get_ror(ticker))
            time.sleep(0.1)
        except Exception as e:
            print(e)
            time.sleep(0.7)

    data = sorted(maps,key= lambda v:(v['value']),reverse=True)
    for i in np.arange(0,15):
        target_prices.append({'ticker':data[i]['ticker'],'price':get_target_price(data[i]['ticker'],data[i]['index'])})
        TICKERS.append(target_prices[i]['ticker'])

def update_possess():
    global possess
    possess = {}
    balances=upbit.get_balances()
    for ticker in balances[2:]:
        possess[TICKERS.index('KRW-'+ticker['currency'])]='KRW-'+ticker['currency']

update_target()
schedule.every(1).hours.do(update_target)

while True:
    schedule.run_pending()
    try:
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        now = datetime.datetime.now()

        all = pyupbit.get_current_price(TICKERS)
        total = get_total()
        krw = upbit.get_balance("KRW")
        cnt=len(upbit.get_balances())-2
        update_possess()
        # j=0
        # cnt1=0
        # for ticker in TICKERS:
        #     print('ticker :',ticker, 'cur_price :',all[ticker],'tar_price :',target_prices[j]['price'])
        #     if(all[ticker]>target_prices[j]['price']):
        #         cnt1+=1
        #     j+=1
        # print(cnt1)

        i=0
        if start_time < now < end_time - datetime.timedelta(minutes=2):
            for ticker in TICKERS:
                if cnt < 2:
                    if target_prices[i]['price'] <= all[ticker] and target_prices[i]['price'] * 1.015 >= all[ticker] and krw > 5000 and upbit.get_balance(ticker) == 0:
                        upbit.buy_market_order(ticker, total*0.199)

                    elif (upbit.get_avg_buy_price(ticker) * 1.05 < all[ticker] or upbit.get_avg_buy_price(ticker) * 0.96 > all[ticker]) and upbit.get_balance(ticker) != 0:
                        upbit.sell_market_order(ticker, upbit.get_balance(ticker))

                    i+=1
                else:
                    if i < max(possess.keys()) and target_prices[i]['price'] <= all[ticker] and target_prices[i]['price'] * 1.015 >= all[ticker] and upbit.get_balance(ticker) == 0:
                        upbit.sell_market_order(possess[max(possess.keys())])
                        time.sleep(0.3)
                        upbit.buy_market_order(ticker, total*0.199)

                    elif (upbit.get_avg_buy_price(ticker) * 1.05 < all[ticker] or upbit.get_avg_buy_price(ticker) * 0.96 > all[ticker]) and upbit.get_balance(ticker) != 0:
                        upbit.sell_market_order(ticker, upbit.get_balance(ticker))

                    i+=1

        else:
            for ticker in TICKERS:
                if upbit.get_balance(ticker) != 0:
                    upbit.sell_market_order(ticker, upbit.get_balance(ticker))
            
        time.sleep(0.05)
    except Exception as e:
        print(e)
        time.sleep(0.5)
