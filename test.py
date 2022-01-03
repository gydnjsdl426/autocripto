import pyupbit

access = "TKLCxLxF0tx8EYN3Z7kWxdToXn0gYfoDny1hCGrE"          # 본인 값으로 변경
secret = "w9xiPT0Ty2p92WG7x1uggrD6qyxR9mtqxC1MV18N"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))    