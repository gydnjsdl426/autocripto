import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
from pytz import timezone, utc

access = "KHTqX6NbkdKaY7saJo40FCjRF8zhLvB2WkADnajD"
secret = "vIIe18R6kquGERglLWfKSC5UxKxfQA6DP4rq2UWc"

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    ma5=df['close'].rolling(5).mean().iloc[-1]
    return ma15 <= ma5 * 1.08

KST=timezone('Asia/Seoul')
now =datetime.datetime.utcnow()
utc.localize(now)
KST.localize(now)
utc.localize(now).astimezone(KST)

predicted_close_price = [0,0,0,0,0,0,0]
def predict_price(ticker, num):
    """Prophet으로 당일 종가 가격 예측"""
    df = pyupbit.get_ohlcv(ticker, interval="minute3", count = 1200)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet(daily_seasonality=20)
    model.fit(data)
    future = model.make_future_dataframe(periods=99, freq = 'min')
    forecast = model.predict(future)
    #현재시간 자정 이전
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds']]
    #자정 이후
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds']]
    predicted_close_price[num] = closeDf['yhat'].values[0]

predict_price("KRW-MATIC",0)
predict_price("KRW-AQT",1)
predict_price("KRW-ETH",2)
predict_price("KRW-POWR",3)
predict_price("KRW-STX",4)
predict_price("KRW-XRP",5)
predict_price("KRW-DOGE",6)

schedule.every(5).minutes.do(predict_price, "KRW-MATIC", 0)
schedule.every(5).minutes.do(predict_price,"KRW-AQT", 1)
schedule.every(5).minutes.do(predict_price, "KRW-ETH", 2)
schedule.every(5).minutes.do(predict_price,"KRW-POWR", 3)
schedule.every(5).minutes.do(predict_price,"KRW-STX", 4)
schedule.every(5).minutes.do(predict_price,"KRW-XRP", 5)
schedule.every(5).minutes.do(predict_price,"KRW-DOGE", 6)

def getTotal():
    aqt = upbit.get_balance("KRW-AQT") * upbit.get_avg_buy_price("KRW-AQT")
    matic = upbit.get_balance("KRW-MATIC") * upbit.get_avg_buy_price("KRW-MATIC")
    eth = upbit.get_balance("KRW-ETH") * upbit.get_avg_buy_price("KRW-ETH")
    powr = upbit.get_balance("KRW-POWR") * upbit.get_avg_buy_price("KRW-POWR")
    stx = upbit.get_balance("KRW-STX") * upbit.get_avg_buy_price("KRW-STX")
    xrp = upbit.get_balance("KRW-XRP") * upbit.get_avg_buy_price("KRW-XRP")
    doge = upbit.get_balance("KRW-DOGE") * upbit.get_avg_buy_price("KRW-DOGE")
    return upbit.get_balance("KRW")+aqt+matic+eth+powr+stx+xrp+doge

def startGamble(name):
    try:
        current_price = pyupbit.get_current_price(name)
        krw = upbit.get_balance("KRW")
        total = getTotal()
        i=0
        for n in name:
            if upbit.get_balance(n) == 0:
                if (current_price[n] * 1.025 <= predicted_close_price[i]) and get_ma15(n) and krw > 5000:
                    upbit.buy_market_order(n, total*0.33)
        
            elif (upbit.get_avg_buy_price(n) * 0.98 >= current_price[n] or (predicted_close_price[i] <= current_price[n] * 0.995 and upbit.get_avg_buy_price(n) * 1.01 <= current_price[n]) or predicted_close_price[i] <= current_price[n] * 0.99):
                upbit.sell_market_order(n, upbit.get_balance(n))

            i=i+1

    except Exception as e:
        print(e)
        time.sleep(1)

# 로그인
upbit = pyupbit.Upbit(access, secret)

# 자동매매 시작
while True:
    schedule.run_pending()
    startGamble(["KRW-MATIC","KRW-AQT","KRW-ETH","KRW-POWR","KRW-STX","KRW-XRP","KRW-DOGE"])
    
