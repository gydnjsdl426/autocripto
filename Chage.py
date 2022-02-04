import time
import pyupbit
import datetime

access = "KHTqX6NbkdKaY7saJo40FCjRF8zhLvB2WkADnajD"
secret = "vIIe18R6kquGERglLWfKSC5UxKxfQA6DP4rq2UWc"

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_total():
    balances = upbit.get_balances()
    total = float(balances[0]['balance'])
    for balance in balances:
        total = float(total) + float(balance['balance']) * float(balance['avg_buy_price'])
    return total

def update_target():
    tickers = pyupbit.get_tickers(fiat="KRW")
    all = pyupbit.get_current_price(tickers)
    i=0
    target_prices=[]
    for ticker in tickers:
        try:
            target_prices.insert(i,get_target_price(ticker, 1.2))
            time.sleep(0.1)
            i += 1
        except Exception as e:
            print(e)
            time.sleep(1)

    return target_prices

target_prices=update_target()

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        tickers = pyupbit.get_tickers(fiat="KRW")
        all = pyupbit.get_current_price(tickers)
        total = get_total()
        krw = upbit.get_balance("KRW") * 0.097
        i=0
        if start_time < now < end_time - datetime.timedelta(seconds=60):
            for ticker in tickers:
                if target_prices[i] < all[ticker] and target_prices[i] * 1.02 > all[ticker] and krw > 5000 and upbit.get_balance(ticker) == 0:
                    upbit.buy_market_order(ticker, total*0.197)
                
                elif upbit.get_avg_buy_price(ticker) * 1.3 < all[ticker] and upbit.get_balance(ticker) != 0:
                    upbit.sell_market_order(ticker, upbit.get_balance(ticker))

                i+=1

        else:
            for ticker in tickers:
                if upbit.get_balance(ticker) != 0:
                    upbit.sell_market_order(ticker, upbit.get_balance(ticker))
            
            target_prices=update_target()

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
