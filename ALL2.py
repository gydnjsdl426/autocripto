import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

access = "KHTqX6NbkdKaY7saJo40FCjRF8zhLvB2WkADnajD"
secret = "vIIe18R6kquGERglLWfKSC5UxKxfQA6DP4rq2UWc"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=7)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    ma5=df['close'].rolling(5).mean().iloc[-1]
    return ma15 <= ma5 * 1.1

predicted_close_price = [0,0,0,0,0,0]
def predict_price(ticker, num):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count = 1440)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=60, freq = 'min')
    forecast = model.predict(future)
    #현재시간 자정 이전
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour = 9)]
    #자정 이후
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour = 9)]
    predicted_close_price[num] = closeDf['yhat'].values[0]

schedule.every().minute.do(lambda: predict_price("KRW-MATIC"), 0)
schedule.every().minute.do(lambda: predict_price("KRW-AQT"), 1)
schedule.every().minute.do(lambda: predict_price("KRW-ETH"), 2)
schedule.every().minute.do(lambda: predict_price("KRW-POWR"), 3)
schedule.every().minute.do(lambda: predict_price("KRW-STX"), 4)
schedule.every().minute.do(lambda: predict_price("KRW-XRP"), 5)

def getTotal():
    aqt = get_balance("AQT") * get_current_price("AQT")
    matic = get_balance("MATIC") * get_current_price("MATIC")
    eth = get_balance("ETH") * get_current_price("ETH")
    powr = get_balance("POWR") * get_current_price("POWR")
    stx = get_balance("STX") * get_current_price("STX")
    xrp = get_balance("XRP") * get_current_price("XRP")
    return get_balance("KRW")+aqt+matic+eth+powr+stx+xrp

def startGamble(name, num):
    try:
        tick=name[4:]
        target_price = get_target_price(name, 0.2)
        current_price = get_current_price(name)
        krw = get_balance("KRW")
        total = getTotal()
        myprice = None
        if get_balance(tick) == 0:
            if target_price < current_price and current_price < predicted_close_price[num] and get_ma15(name) and krw > 5000:
                upbit.buy_market_order(name, total*0.1665)
        
        elif upbit.get_avg_buy_price(name) * 0.965 > current_price or upbit.get_avg_buy_price(name) * 1.3 < current_price or (predicted_close_price[num] < current_price and upbit.get_avg_buy_price(name) * 1.03 < current_price):
            upbit.sell_market_order(name, get_balance(tick))

    except Exception as e:
        print(e)
        time.sleep(1)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    startGamble("KRW-MATIC", 0)
    startGamble("KRW-AQT", 1)
    startGamble("KRW-ETH" ,2)
    startGamble("KRW-POWR", 3)
    startGamble("KRW-STX", 4)
    startGamble("KRW-XRP", 5)
    
