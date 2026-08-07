#Replit
#binence api
#Replit
import calendar
import decimal
from datetime import datetime, timedelta
from decimal import Decimal
import math
import os
import re
import time
from binance.client import Client
import numpy
import pandas as pd
import pytz
import requests

invest_usdt = 4
retry_num = 3
check_order_list = []

##############################################################################
##############################################################################
kst = pytz.timezone("Asia/Seoul")
time_str = "2026-07-02,11:30"
dt = datetime.strptime(time_str, "%Y-%m-%d,%H:%M")
dt = kst.localize(dt)
origin_time = int(dt.timestamp() * 1000)

##############################################################################
reset_time = int((int(time.time()) - (7 * 24 * 60 * 60)) * 1000)
limit_time = int((int(time.time()) - (6 * 24 * 60 * 60)) * 1000)
final_time = int((int(time.time()) - (5 * 24 * 60 * 60)) * 1000)

if origin_time >= reset_time:
    start_time = origin_time
else:
    start_time = reset_time

##############################################################################
##############################################################################
chat_id = os.getenv("chat_id")
order_id = os.getenv("order_id")

# 바이낸스 클라이언트 생성 (시세 조회 등 Public API는 API Key 없이도 작동합니다)
# API Key가 필요한 경우: Client(api_key=os.getenv("BINANCE_KEY"), api_secret=os.getenv("BINANCE_SECRET"))
client = Client()
try_list = []
avail_order_num = 25
##############################################################################
# 바이낸스 USDT-M 선물 24시간 티커 데이터 조회
tickers = client.futures_ticker()
time.sleep(1)
df = pd.DataFrame(tickers)
# USDT 선물 심볼만 추출
df = df[df['symbol'].str.endswith('USDT')].copy()
# 컬럼 타입 및 단위 보정
# quoteVolume: 24시간 거래대금 (USDT 기준)
# priceChangePercent: 24시간 변동률 (%) -> 바이비트 스타일 소수점으로 변환
df['turnover24h'] = df['quoteVolume'].astype(float)
df['lastPrice'] = df['lastPrice'].astype(float)
df['price24hPcnt'] = df['priceChangePercent'].astype(float) / 100.0
# 거래대금(turnover24h) 내림차순 정렬
sort_list = df.sort_values(
    'turnover24h', key=lambda x: x.abs(), ascending=False, ignore_index=True
)
# 조건 필터링: 현재가가 (invest_usdt * 2) 미만인 종목
added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
added_symbols = added_list["symbol"].tolist()
# -------------------------------------------------------------------------
# 2. 바이낸스 상장 폐지 / 거래 정지 심볼 제외 로직
# -------------------------------------------------------------------------
final_del_list = []
try:
    # 방법 A: 바이낸스 선물 거래소 정보(Exchange Info)에서 TRADING 상태가 아닌 심볼 수집
    exchange_info = client.futures_exchange_info()
    inactive_symbols = [
        s['symbol']
        for s in exchange_info['symbols']
        if s['status'] != 'TRADING'
    ]
    final_del_list.extend(inactive_symbols)
    # 방법 B: 바이낸스 공식 공지사항(Announcements) API 파싱 (Delisting 키워드 검색)
    ann_url = "https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query?catalogId=48&pageNo=1&pageSize=10"
    res = requests.get(ann_url, timeout=5).json()
    articles = res.get('data', {}).get('articles', [])
    del_titles = [
        a['title']
        for a in articles
        if 'Delist' in a['title'] or 'delist' in a['title']
    ]
    all_words = []
    for title in del_titles:
        all_words.extend(re.findall(r'\b\w+\b', title))
    # 대문자 단어 추출 (e.g. BTC, ETH 등 심볼명)
    uppercase_words = {word for word in all_words if word.isupper()}
    final_del_list.extend(list(uppercase_words))
    final_del_list = sorted(list(set(final_del_list)))
except Exception as e:
    print(f"상장 폐지 공지 조회 실패 (스킵): {e}")
    final_del_list = []
# -------------------------------------------------------------------------
# 3. 제외 대상 정제 및 최종 try_list 확장
# -------------------------------------------------------------------------
# 1) 이미 보유/주문 시도 중인 try_list 제외
added_symbols = [x for x in added_symbols if x not in try_list]
# 2) 상장 폐지/거래 정지 대상 심볼 및 키워드 포함 심볼 제외
added_symbols = [
    x
    for x in added_symbols
    if x not in final_del_list
    and not any(del_word in x for del_word in final_del_list)
]
# 3) USDT 페어만 최종 확인
added_symbols = [x for x in added_symbols if 'USDT' in x]
time.sleep(1)
print('added_symbols (필터링 후):', len(added_symbols))
# 추가할 수량 설정 및 try_list 확장
added_num = avail_order_num + 5
added_symbols = added_symbols[:added_num]
if added_symbols:
    try_list.extend(added_symbols)
print('added_symbols (최종 추가):', len(try_list))
print(try_list)
################################################################################
def search_calc(sym_bol):
  order_position = 9
  itv_list = ['3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h']
  for itv in itv_list:
#-------------------------------------------------------------------------------
    get_kline = client.futures_klines(symbol=sym_bol, interval=itv, limit=1000)
# DataFrame 변환 및 컬럼 지정
    cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'turnover', 'trades', 'tb_base', 'tb_quote', 'ignore']
    df_kline = pd.DataFrame(get_kline, columns=cols)
# 필요한 컬럼 타입 변환
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'turnover']
    df_kline[numeric_cols] = df_kline[numeric_cols].astype(float)
    df_kline['timestamp'] = df_kline['timestamp'].astype(int)
# 바이비트 스타일(최신순)로 맞추려면:
    df_kline = df_kline.iloc[::-1].reset_index(drop=True)
# 리스트로 추출이 필요한 경우:
    t_list = df_kline['timestamp'].tolist()
    o_list = df_kline['open'].tolist()
    h_list = df_kline['high'].tolist()
    l_list = df_kline['low'].tolist()
    c_list = df_kline['close'].tolist()
    v_list = df_kline['volume'].tolist()
    p_list = df_kline['turnover'].tolist()
#-------------------------------------------------------------------------------
    max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
    sta = 0
    max_diff = c_list[sta] * 0.5 / max_lever
    min_diff = c_list[sta] * 0.5 / min_lever
    cal_max, cal_min = max(h_list[sta:]), min(l_list[sta:])
    xnum = h_list[sta:].index(cal_max) + sta
    nnum = l_list[sta:].index(cal_min) + sta
    cal_diff = cal_max - cal_min
    cal_lever = c_list[sta] * 0.5 / cal_diff
    limit_diff = cal_diff
    for std in range(sta,len(t_list)):
        if(h_list[std] >= c_list[sta] >= l_list[std]):
            std_max, std_min = max(h_list[sta:std+1]), min(l_list[sta:std+1])
            std_diff = std_max - std_min
            std_x_diff, std_n_diff = abs(c_list[sta] - std_max), abs(c_list[sta] - std_min)
            std_min_diff, std_max_diff = min(std_n_diff, std_x_diff), max(std_n_diff, std_x_diff)
            xnum = h_list[sta:].index(std_max) + sta
            nnum = l_list[sta:].index(std_min) + sta
            if(std_min_diff > min_diff) and (std not in (xnum, nnum)):
                for bk in range(std,len(t_list)):
                    bk_max, bk_min = max(h_list[std:bk+1]), min(l_list[std:bk+1])
                    bk_x_diff, bk_n_diff = abs(c_list[std] - bk_max), abs(c_list[std] - bk_min)
                    bx_num = h_list[std:].index(bk_max) + std
                    bn_num = l_list[std:].index(bk_min) + std
                    if(max(bk_x_diff, bk_n_diff) >= std_max_diff): break
                upper_v, lower_v = 0, 0
                for vol in range(sta,std+1):
                    if(c_list[sta] > h_list[vol]): lower_v = lower_v + v_list[vol]
                    elif(c_list[sta] < l_list[vol]): upper_v = upper_v + v_list[vol]
                    else:
                      if(h_list[vol] != l_list[vol]):
                          upper_v = upper_v + (abs(c_list[sta] - h_list[vol]) / (h_list[vol] - l_list[vol]) * v_list[vol])
                          lower_v = lower_v + (abs(c_list[sta] - l_list[vol]) / (h_list[vol] - l_list[vol]) * v_list[vol])
                vol_per = lower_v / (upper_v + lower_v) * 100
                if((max(bx_num, bn_num) + 1) >= len(t_list)): order_position = 0
                else:
                    xnum = h_list[sta:].index(std_max) + sta
                    nnum = l_list[sta:].index(std_min) + sta
                    if(vol_per > 75) and (xnum > nnum): order_position = 11
                    if(vol_per < 25) and (xnum < nnum): order_position = 22
                    if(order_position == 11) and (bx_num < bn_num): order_position = 1
                    if(order_position == 11) and (bx_num > bn_num): order_position = 4
                    if(order_position == 22) and (bx_num < bn_num): order_position = 3
                    if(order_position == 22) and (bx_num > bn_num): order_position = 2
                    std_per = round(std_max_diff / (max_diff * 3) * 100, 2)
                    if(order_position in (1, 2, 3, 4, 11, 22)) and (std_max_diff > (max_diff * 3)): order_position = 5 
        if(order_position not in (0, 9)):
            print(sym_bol, itv, order_position, round(vol_per, 2), std_per)
            break
    if(cal_diff > (max_diff * 4)): break
    if(order_position in (0, 9)): continue
    cal_diff = std_max_diff
    cal_lever = c_list[sta] * 0.5 / cal_diff
    limit_diff = cal_diff
    if(cal_diff > max_diff): limit_diff = max_diff
    break
  if(order_position == 9): print(sym_bol, itv, order_position)
#-------------------------------------------------------------------------------
  order_return = [order_position]
  return(order_return)
for sym_bol in try_list:
  order_return = search_calc(sym_bol)      
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
#bybit api
from pybit.unified_trading import HTTP
import pandas as pd
import time
from datetime import datetime, timedelta
import calendar
import pytz
import decimal
import re
import requests
import math
import numpy
from decimal import Decimal
import os

invest_usdt = 4
retry_num = 3
check_order_list = []
##############################################################################
##############################################################################
kst = pytz.timezone("Asia/Seoul")
time_str = "2026-07-02,11:30"
dt = datetime.strptime(time_str, "%Y-%m-%d,%H:%M")
dt = kst.localize(dt)
origin_time = int(dt.timestamp() * 1000)
##############################################################################
reset_time = int((int(time.time()) - (7 * 24 * 60 * 60)) * 1000)
limit_time = int((int(time.time()) - (6 * 24 * 60 * 60)) * 1000)
final_time = int((int(time.time()) - (5 * 24 * 60 * 60)) * 1000)
#start_time = int(int(time.time()) * 1000)
if(origin_time >= reset_time): start_time = origin_time
else: start_time = reset_time
##############################################################################
##############################################################################
chat_id = os.getenv("chat_id")
order_id = os.getenv("order_id")
session = HTTP(
    testnet=False,
    max_retries=10,
    retry_delay=15,
  )
##############################################################################
tickers = session.get_tickers(category="linear")['result']['list']
time.sleep(1)
df = pd.DataFrame(tickers)
df['turnover24h'] = df['turnover24h'].astype(float)
df['lastPrice'] = df['lastPrice'].astype(float)
df['price24hPcnt'] = df['price24hPcnt'].astype(float)
trun_list = df.sort_values('turnover24h', key=lambda x: x.abs(), ascending=False, ignore_index=True)
trun_symbols = trun_list["symbol"].tolist()
added_trun = trun_list[(trun_list['lastPrice'] < (invest_usdt * 2))]

added_symbols1 = added_trun["symbol"].tolist()
added_symbols2 = added_trun["price24hPcnt"].tolist()
added_symbols3 = added_trun["turnover24h"].tolist()
#print(added_symbols1[:30])
#print(added_symbols3[:30])
#print(added_symbols2[:30])
added_symbols = added_symbols1.copy()
sort_list = df.sort_values('price24hPcnt', key=lambda x: x.abs(), ascending=False, ignore_index=True)
sort_symbols = sort_list["symbol"].tolist()
print(len(sort_symbols))
added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
added_symbols1 = added_list["symbol"].tolist()
added_symbols2 = added_list["price24hPcnt"].tolist()
added_symbols3 = added_list["turnover24h"].tolist()
#print(added_symbols1[:30])
#print(added_symbols3[:30])
#print(added_symbols2[:30])
#added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e7)]
#  added_list = sort_list[(sort_list['lastPrice'] > 0.01) & (sort_list['lastPrice'] < 2) & (sort_list['turnover24h'] > 3e+07)]
#  added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
#added_symbols = added_list["symbol"].tolist()
#print(added_symbols)
################################################################################
def search_calc(sym_bol):
  order_position = 9
  itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
  for itv in itv_list:
#-------------------------------------------------------------------------------
    get_kline=session.get_kline(category="linear",symbol=sym_bol,interval=str(itv),limit=1000)['result']['list']
    time.sleep(1)
    kline = pd.DataFrame(get_kline)
    t_list,o_list,h_list,l_list,c_list,v_list,p_list = [],[],[],[],[],[],[]
    for i in range(len(kline[0])):
      t_list.append(int(kline[0][i]))
      o_list.append(float(kline[1][i]))
      h_list.append(float(kline[2][i]))
      l_list.append(float(kline[3][i]))
      c_list.append(float(kline[4][i]))
      v_list.append(float(kline[5][i]))
      p_list.append(float(kline[6][i]))
#-------------------------------------------------------------------------------
    max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
    sta = 0
    max_diff = c_list[sta] * 0.5 / max_lever
    min_diff = c_list[sta] * 0.5 / min_lever
    cal_max, cal_min = max(h_list[sta:]), min(l_list[sta:])
    xnum = h_list[sta:].index(cal_max) + sta
    nnum = l_list[sta:].index(cal_min) + sta
    cal_diff = cal_max - cal_min
    cal_lever = c_list[sta] * 0.5 / cal_diff
    limit_diff = cal_diff
    for std in range(sta,len(t_list)):
        if(h_list[std] >= c_list[sta] >= l_list[std]):
            std_max, std_min = max(h_list[sta:std+1]), min(l_list[sta:std+1])
            std_diff = std_max - std_min
            std_x_diff, std_n_diff = abs(c_list[sta] - std_max), abs(c_list[sta] - std_min)
            std_min_diff, std_max_diff = min(std_n_diff, std_x_diff), max(std_n_diff, std_x_diff)
            xnum = h_list[sta:].index(std_max) + sta
            nnum = l_list[sta:].index(std_min) + sta
            if(std_min_diff > min_diff) and (std not in (xnum, nnum)):
                for bk in range(std,len(t_list)):
                    bk_max, bk_min = max(h_list[std:bk+1]), min(l_list[std:bk+1])
                    bk_x_diff, bk_n_diff = abs(c_list[std] - bk_max), abs(c_list[std] - bk_min)
                    bx_num = h_list[std:].index(bk_max) + std
                    bn_num = l_list[std:].index(bk_min) + std
                    if(max(bk_x_diff, bk_n_diff) >= std_max_diff): break
                upper_v, lower_v = 0, 0
                for vol in range(sta,std+1):
                    if(c_list[sta] > h_list[vol]): lower_v = lower_v + v_list[vol]
                    elif(c_list[sta] < l_list[vol]): upper_v = upper_v + v_list[vol]
                    else:
                      if(h_list[vol] != l_list[vol]):
                          upper_v = upper_v + (abs(c_list[sta] - h_list[vol]) / (h_list[vol] - l_list[vol]) * v_list[vol])
                          lower_v = lower_v + (abs(c_list[sta] - l_list[vol]) / (h_list[vol] - l_list[vol]) * v_list[vol])
                vol_per = lower_v / (upper_v + lower_v) * 100
                if((max(bx_num, bn_num) + 1) >= len(t_list)): order_position = 0
                else:
                    xnum = h_list[sta:].index(std_max) + sta
                    nnum = l_list[sta:].index(std_min) + sta
                    if(vol_per > 75) and (xnum > nnum): order_position = 11
                    if(vol_per < 25) and (xnum < nnum): order_position = 22
                    if(order_position == 11) and (bx_num < bn_num): order_position = 1
                    if(order_position == 11) and (bx_num > bn_num): order_position = 4
                    if(order_position == 22) and (bx_num < bn_num): order_position = 3
                    if(order_position == 22) and (bx_num > bn_num): order_position = 2
                    std_per = round(std_max_diff / (max_diff * 3) * 100, 2)
                    if(order_position in (1, 2, 3, 4, 11, 22)) and (std_max_diff > (max_diff * 3)): order_position = 5 
        if(order_position not in (0, 9)):
            print(sym_bol, itv, order_position, round(vol_per, 2), std_per)
            break
    if(cal_diff > (max_diff * 4)): break
    if(order_position in (0, 9)): continue
    cal_diff = std_max_diff
    cal_lever = c_list[sta] * 0.5 / cal_diff
    limit_diff = cal_diff
    if(cal_diff > max_diff): limit_diff = max_diff
    break
  if(order_position == 9): print(sym_bol, itv, order_position)
#-------------------------------------------------------------------------------
  order_return = [order_position]
  return(order_return)
for sym_bol in added_symbols[:30]:
  order_return = search_calc(sym_bol)      
##############################################################################
# def search_calc(sym_bol):
#   order_position = 9
#   itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
#   for itv in itv_list:
# #-------------------------------------------------------------------------------
#     get_kline=session.get_kline(category="linear",symbol=sym_bol,interval=str(itv),limit=1000)['result']['list']
#     time.sleep(1)
#     kline = pd.DataFrame(get_kline)
#     t_list,o_list,h_list,l_list,c_list,v_list,p_list = [],[],[],[],[],[],[]
#     for i in range(len(kline[0])):
#       t_list.append(int(kline[0][i]))
#       o_list.append(float(kline[1][i]))
#       h_list.append(float(kline[2][i]))
#       l_list.append(float(kline[3][i]))
#       c_list.append(float(kline[4][i]))
#       v_list.append(float(kline[5][i]))
#       p_list.append(float(kline[6][i]))
# #-------------------------------------------------------------------------------
#     max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
#     sta = 100
#     max_diff = c_list[sta] * 0.5 / max_lever
#     min_diff = c_list[sta] * 0.5 / min_lever
#     cal_max, cal_min = max(h_list[sta:]), min(l_list[sta:])
#     xnum = h_list[sta:].index(cal_max) + sta
#     nnum = l_list[sta:].index(cal_min) + sta
#     cal_diff = cal_max - cal_min
#     cal_lever = c_list[sta] * 0.5 / cal_diff
#     limit_diff = cal_diff
#     for std in range(sta,len(t_list)):
#         if(h_list[std] >= c_list[sta] >= l_list[std]):
#             std_max, std_min = max(h_list[sta:std+1]), min(l_list[sta:std+1])
#             std_diff = std_max - std_min
#             std_x_diff, std_n_diff = abs(c_list[sta] - std_max), abs(c_list[sta] - std_min)
#             std_min_diff, std_max_diff = min(std_n_diff, std_x_diff), max(std_n_diff, std_x_diff)
#             if(std_min_diff > min_diff):
#                 upper_v, lower_v = 0, 0
#                 for vol in range(sta,std+1):
#                     if(c_list[sta] > h_list[vol]): lower_v = lower_v + v_list[vol]
#                     elif(c_list[sta] < l_list[vol]): upper_v = upper_v + v_list[vol]
#                     else:
#                       if(h_list[vol] != l_list[vol]):
#                           upper_v = upper_v + (abs(c_list[sta] - h_list[vol]) / (h_list[vol] - l_list[vol]) * v_list[vol])
#                           lower_v = lower_v + (abs(c_list[sta] - l_list[vol]) / (h_list[vol] - l_list[vol]) * v_list[vol])
#                 vol_per = lower_v / (upper_v + lower_v) * 100
#                 if(vol_per > 75): order_position = 11
#                 if(vol_per < 25): order_position = 22
#                 xnum = h_list[sta:].index(std_max) + sta
#                 nnum = l_list[sta:].index(std_min) + sta
#                 if(order_position == 11) and (xnum > nnum): order_position = 1
#                 if(order_position == 22) and (xnum < nnum): order_position = 1
#         if(order_position in (1, 2, 11, 22)): break
# #    if(order_position not in (1, 2)) and (std_max_diff > (max_diff * 2)):
# #        print(sym_bol, itv, "pass", vol_per)
# #        break
#     if(order_position not in (1, 2, 11, 22)): continue
#     std_n_lever = round(c_list[sta] * 0.5 / std_n_diff, 2)
#     std_x_lever = round(c_list[sta] * 0.5 / std_x_diff, 2)
#     std_max_lever = round(c_list[sta] * 0.5 / std_diff, 2)
#     std_per = round((c_list[sta] - std_min) / (std_max - std_min) * 100, 2)

#     upper_v, lower_v = 0, 0
#     for new in range(std+1):
#         if(c_list[0] > h_list[new]): lower_v = lower_v + v_list[new]
#         elif(c_list[0] < l_list[new]): upper_v = upper_v + v_list[new]
#         else:
#             if(h_list[new] != l_list[new]):
#                 upper_v = upper_v + (abs(c_list[0] - h_list[new]) / (h_list[new] - l_list[new]) * v_list[new])
#                 lower_v = lower_v + (abs(c_list[0] - l_list[new]) / (h_list[new] - l_list[new]) * v_list[new])
#     new_per = lower_v / (upper_v + lower_v) * 100
#     upper_per = round(abs(c_list[sta] - max(h_list[:sta+1])) * min(std_n_lever, std_x_lever) / c_list[sta], 2)
#     lower_per = round(abs(c_list[sta] - min(l_list[:sta+1])) * min(std_n_lever, std_x_lever) / c_list[sta], 2)
#     if(cal_diff > max_diff): limit_diff = max_diff
#     print(sym_bol, itv, order_position, round(vol_per, 2), round(new_per, 2))
#     print(std_x_lever, std_n_lever, std_max_lever, std_per)
#     print(c_list[sta], max(h_list[:sta+1]), min(l_list[:sta+1]), c_list[0], upper_per, lower_per)
#     break
# #-------------------------------------------------------------------------------
#   order_return = [order_position]
#   return(order_return)
# for sym_bol in added_symbols[:30]:
#   order_return = search_calc(sym_bol)      
##############################################################################
# def search_calc(sym_bol):
#   order_position = 9
#   itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
#   for itv in itv_list:
# #-------------------------------------------------------------------------------
#     get_kline=session.get_kline(category="linear",symbol=sym_bol,interval=str(itv),limit=1000)['result']['list']
#     time.sleep(1)
#     kline = pd.DataFrame(get_kline)
#     t_list,o_list,h_list,l_list,c_list,v_list,p_list = [],[],[],[],[],[],[]
#     for i in range(len(kline[0])):
#       t_list.append(int(kline[0][i]))
#       o_list.append(float(kline[1][i]))
#       h_list.append(float(kline[2][i]))
#       l_list.append(float(kline[3][i]))
#       c_list.append(float(kline[4][i]))
#       v_list.append(float(kline[5][i]))
#       p_list.append(float(kline[6][i]))
# #-------------------------------------------------------------------------------
#     max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
#     sta = 100
#     max_diff = c_list[sta] * 0.5 / max_lever
#     min_diff = c_list[sta] * 0.5 / min_lever
#     cal_max, cal_min = max(h_list[sta:]), min(l_list[sta:])
#     xnum = h_list[sta:].index(cal_max) + sta
#     nnum = l_list[sta:].index(cal_min) + sta
#     cal_diff = cal_max - cal_min
#     cal_lever = c_list[sta] * 0.5 / cal_diff
#     limit_diff = cal_diff
#     for fr in range(sta,len(t_list)):
#         fr_max, fr_min = max(h_list[sta:fr+1]), min(l_list[sta:fr+1])
#         fr_x_diff, fr_n_diff = abs(c_list[sta] - fr_max), abs(c_list[sta] - fr_min)
#         fr_min_diff, fr_max_diff = min(fr_n_diff, fr_x_diff), max(fr_n_diff, fr_x_diff)
#         if(fr_min_diff > min_diff) and ((fr_max_diff * 0.5) > fr_min_diff):
#             order_position = 0
#             break
#     xnum = h_list[sta:].index(fr_max) + sta
#     nnum = l_list[sta:].index(fr_min) + sta
#     if(order_position == 0):
#       for bk in range(fr,len(t_list)):
#         bk_max, bk_min = max(h_list[fr:bk+1]), min(l_list[fr:bk+1])
#         if(nnum > xnum) and (bk_max >= c_list[0]): order_position = 3
#         if(nnum < xnum) and (bk_min <= c_list[0]): order_position = 3
#         if(order_position == 3): break
#     if(nnum == xnum): break
#     if(order_position == 3):
#         std_max, std_min = max(h_list[sta:bk+1]), min(l_list[sta:bk+1])
#         xnum = h_list[sta:].index(std_max) + sta
#         nnum = l_list[sta:].index(std_min) + sta
#         upper_v, lower_v = 0, 0
#         for std in range(sta,bk+1):
#             if(c_list[sta] > h_list[std]): lower_v = lower_v + v_list[std]
#             elif(c_list[sta] < l_list[std]): upper_v = upper_v + v_list[std]
#             else:
#               if(h_list[std] != l_list[std]):
#                   upper_v = upper_v + (abs(c_list[sta] - h_list[std]) / (h_list[std] - l_list[std]) * v_list[std])
#                   lower_v = lower_v + (abs(c_list[sta] - l_list[std]) / (h_list[std] - l_list[std]) * v_list[std])
#         vol_per = lower_v / (upper_v + lower_v) * 100

#         upper_v, lower_v = 0, 0
#         for std in range(bk+1):
#             if(c_list[0] > h_list[std]): lower_v = lower_v + v_list[std]
#             elif(c_list[0] < l_list[std]): upper_v = upper_v + v_list[std]
#             else:
#               if(h_list[std] != l_list[std]):
#                   upper_v = upper_v + (abs(c_list[0] - h_list[std]) / (h_list[std] - l_list[std]) * v_list[std])
#                   lower_v = lower_v + (abs(c_list[0] - l_list[std]) / (h_list[std] - l_list[std]) * v_list[std])
#         new_per = lower_v / (upper_v + lower_v) * 100
        
#         std_x_diff, std_n_diff = abs(c_list[sta] - std_max), abs(c_list[sta] - std_min)
#         if(std_x_diff > std_n_diff) and ((std_x_diff * 0.5) > std_n_diff): order_position = 2
#         if(std_x_diff < std_n_diff) and ((std_n_diff * 0.5) > std_x_diff): order_position = 1
#         cal_diff = min(std_n_diff, std_x_diff)
#         cal_lever = c_list[sta] * 0.5 / cal_diff
#         limit_diff = cal_diff
#         if(cal_diff > max_diff): limit_diff = max_diff
#         cal_max, cal_min = std_max, std_min
#         cal_per = round((c_list[sta] - cal_min) / (cal_max - cal_min) * 100, 2)
#     if(order_position in (0, 9)): continue
#     limit_diff = cal_diff
#     if(cal_diff > max_diff): limit_diff = max_diff
# #    limit_diff = max_diff
#     print(sym_bol, itv, order_position, round(vol_per, 2), round(new_per, 2))
#     print(c_list[sta], max(h_list[:sta+1]), min(l_list[:sta+1]), c_list[0])
#     break
# #-------------------------------------------------------------------------------
#   order_return = [order_position]
#   return(order_return)
# for sym_bol in added_symbols[:30]:
#   order_return = search_calc(sym_bol)      
##############################################################################
# def search_calc(sym_bol, accum_num):
#   order_position = 9
#   itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
#   for itv in itv_list:
# #-------------------------------------------------------------------------------
#     get_kline=session.get_kline(category="linear",symbol=sym_bol,interval=str(itv),limit=1000)['result']['list']
#     time.sleep(1)
#     kline = pd.DataFrame(get_kline)
#     t_list,o_list,h_list,l_list,c_list,v_list,p_list = [],[],[],[],[],[],[]
#     for i in range(len(kline[0])):
#       t_list.append(int(kline[0][i]))
#       o_list.append(float(kline[1][i]))
#       h_list.append(float(kline[2][i]))
#       l_list.append(float(kline[3][i]))
#       c_list.append(float(kline[4][i]))
#       v_list.append(float(kline[5][i]))
#       p_list.append(float(kline[6][i]))
# #-------------------------------------------------------------------------------
#     max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
#     sta = 0
#     max_diff = c_list[sta] * 0.5 / max_lever
#     min_diff = c_list[sta] * 0.5 / min_lever
#     cal_max, cal_min = max(h_list[sta:]), min(l_list[sta:])
#     xnum = h_list[sta:].index(cal_max) + sta
#     nnum = l_list[sta:].index(cal_min) + sta
#     cal_diff = cal_max - cal_min
#     cal_lever = c_list[sta] * 0.5 / cal_diff
#     for std in range(sta,len(t_list)):
#       if(nnum > xnum):
#         std_max, std_min = max(h_list[sta:xnum+1]), min(l_list[sta:xnum+1])
#         xnum = h_list[sta:].index(std_max) + sta
#         nnum = l_list[sta:].index(std_min) + sta
#         if(nnum == xnum): break
#         std_diff = std_max - std_min
#         std_lever = c_list[sta] * 0.5 / std_diff
#         print(sym_bol, itv, round(std_lever, 2))
#         if(std_diff < min_diff): break
#         for bk in range(xnum, len(t_list)):
#             if(l_list[bk] <= std_min): break
#         if(h_list[bk] == l_list[bk]): st_vol = v_list[bk]
#         else: st_vol = v_list[bk] * abs((h_list[bk] - std_min) / (h_list[bk] - l_list[bk]))
#         bk_vol = sum(v_list[xnum:bk]) + st_vol
#         fr_vol = sum(v_list[sta:xnum])
#         fr_per = fr_vol / bk_vol * 100
#         order_position = 22
#         if(fr_per < 100): order_position = 2
#         cal_max, cal_min, cal_diff, cal_lever = std_max, std_min, std_diff, std_lever
#         print(sym_bol, itv, round(cal_lever, 2), round(fr_per, 2))
#         print(order_position, xnum, nnum, bk, h_list[xnum], l_list[nnum], h_list[std])
#         continue
#       if(nnum < xnum):
#         std_max, std_min = max(h_list[sta:nnum+1]), min(l_list[sta:nnum+1])
#         xnum = h_list[sta:].index(std_max) + sta
#         nnum = l_list[sta:].index(std_min) + sta
#         if(nnum == xnum): break
#         std_diff = std_max - std_min
#         std_lever = c_list[sta] * 0.5 / std_diff
#         print(sym_bol, itv, round(std_lever, 2))
#         if(std_diff < min_diff): break
#         for bk in range(nnum, len(t_list)):
#             if(h_list[bk] >= std_max): break
#         if(h_list[bk] == l_list[bk]): st_vol = v_list[bk]
#         else: st_vol = v_list[bk] * abs((std_max - l_list[bk]) / (h_list[bk] - l_list[bk]))
#         bk_vol = sum(v_list[nnum:bk]) + st_vol
#         fr_vol = sum(v_list[sta:nnum])
#         fr_per = fr_vol / bk_vol * 100
#         order_position = 11
#         if(fr_per < 100): order_position = 1
#         cal_max, cal_min, cal_diff, cal_lever = std_max, std_min, std_diff, std_lever
#         print(sym_bol, itv, round(cal_lever, 2), round(fr_per, 2))
#         print(order_position, xnum, nnum, bk, h_list[xnum], l_list[nnum], h_list[std])
#         continue
#       if(nnum == xnum): break
#     if(order_position == 9): continue
#     limit_idff = cal_diff
#     if(cal_diff > max_diff): limit_idff = max_diff
#     break
#-------------------------------------------------------------------------------
#   order_return = [order_position]
#   return(order_return)
# for sym_bol in added_symbols[:30]:
#   order_return = search_calc(sym_bol)
# ##############################################################################
# def search_calc(sym_bol):
#   order_position = 9
#   itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
#   for itv in itv_list:
# #-------------------------------------------------------------------------------
#     get_kline=session.get_kline(category="linear",symbol=sym_bol,interval=str(itv),limit=1000)['result']['list']
#     time.sleep(1)
#     kline = pd.DataFrame(get_kline)
#     t_list,o_list,h_list,l_list,c_list,v_list,p_list = [],[],[],[],[],[],[]
#     for i in range(len(kline[0])):
#       t_list.append(int(kline[0][i]))
#       o_list.append(float(kline[1][i]))
#       h_list.append(float(kline[2][i]))
#       l_list.append(float(kline[3][i]))
#       c_list.append(float(kline[4][i]))
#       v_list.append(float(kline[5][i]))
#       p_list.append(float(kline[6][i]))
# #-------------------------------------------------------------------------------
#     max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
#     sta = 0
#     max_diff = c_list[sta] * 0.5 / max_lever
#     min_diff = c_list[sta] * 0.5 / min_lever
#     std_max, std_min = max(c_list[sta:]), min(c_list[sta:])
#     xnum = c_list[sta:].index(std_max) + sta
#     nnum = c_list[sta:].index(std_min) + sta
#     max_vol = sum(v_list[min(xnum, nnum):max(xnum, nnum)+1])
#     le_diff = std_max - std_min
#     limit_diff = le_diff
#     std_diff = le_diff / max_vol
#     std_vol = max_vol / le_diff
#     h_num, l_num = 0, 0
#     for std in range(sta,len(t_list)):
#         cal_max, cal_min = max(h_list[sta:std+1]), min(l_list[sta:std+1])
#         h_diff = cal_max - c_list[sta]
#         l_diff = c_list[sta] - cal_min
#         if(h_num == 0) and (max_diff >= h_diff >= min_diff) and (l_list[0] <= min(l_list[:std+1])): h_num = std
#         if(l_num == 0) and (max_diff >= l_diff >= min_diff) and (h_list[0] >= max(h_list[:std+1])): l_num = std
#         if(h_num != 0) or (l_num != 0): break
#     if(h_num == 0) and (l_num == 0):
#       if(max(h_diff, l_diff) > max_diff):
#         print(sym_bol, itv)
#         break
#       else: continue

#     if(h_num != 0):
#       for h_std in range(h_num, len(t_list)):
#         if(l_list[h_std] <= c_list[sta]):
#           order_position = 11
#           break
#     if(order_position == 11):
#           fr_max = max(h_list[sta:h_std+1])
#           fr_num = h_list[sta:].index(fr_max) + sta
#           fr_vol = sum(v_list[sta:fr_num])
#           ba_vol = sum(v_list[fr_num:h_std+1])
#           fr_per = fr_vol / ba_vol * 100
#           cal_diff = fr_max - c_list[sta]
#           cal_lever = c_list[sta] * 0.5 / cal_diff
#           limit_diff = cal_diff
#           if(fr_per > 100) and (max_lever <= cal_lever <= min_lever): order_position = 1
#           if(fr_per < 100) and (max_lever <= cal_lever <= min_lever): order_position = 3
#           print(sym_bol, itv, round(cal_lever, 2), round(fr_per, 2))

#     if(l_num != 0):
#       for l_std in range(l_num, len(t_list)):
#         if(h_list[l_std] >= c_list[sta]):
#           order_position = 22
#           break
#     if(order_position == 22):
#           fr_max = min(l_list[sta:l_std+1])
#           fr_num = l_list[sta:].index(fr_max) + sta
#           fr_vol = sum(v_list[sta:fr_num])
#           ba_vol = sum(v_list[fr_num:l_std+1])
#           fr_per = fr_vol / ba_vol * 100
#           cal_diff = abs(fr_max - c_list[sta])
#           cal_lever = c_list[sta] * 0.5 / cal_diff
#           limit_diff = cal_diff
#           if(fr_per < 100) and (max_lever <= cal_lever <= min_lever): order_position = 3
#           if(fr_per > 100) and (max_lever <= cal_lever <= min_lever): order_position = 2
#           print(sym_bol, itv, round(cal_lever, 2), round(fr_per, 2))
#     if(min(h_diff, l_diff) > max_diff): break
#     if(order_position == 9): continue
#     break
# #-------------------------------------------------------------------------------
#   order_return = [order_position]
#   return(order_return)
# for sym_bol in added_symbols[:30]:
#   order_return = search_calc(sym_bol)
# ##############################################################################
# def search_calc(sym_bol):
#       order_position = 9
#       itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
#       for itv in itv_list:
#     #-------------------------------------------------------------------------------
#         get_kline=session.get_kline(category="linear",symbol=sym_bol,interval=str(itv),limit=1000)['result']['list']
#         time.sleep(1)
#         kline = pd.DataFrame(get_kline)
#         t_list,o_list,h_list,l_list,c_list,v_list,p_list = [],[],[],[],[],[],[]
#         for i in range(len(kline[0])):
#           t_list.append(int(kline[0][i]))
#           o_list.append(float(kline[1][i]))
#           h_list.append(float(kline[2][i]))
#           l_list.append(float(kline[3][i]))
#           c_list.append(float(kline[4][i]))
#           v_list.append(float(kline[5][i]))
#           p_list.append(float(kline[6][i]))
#     #-------------------------------------------------------------------------------
#         max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
#         sta = 50
#         max_diff = c_list[sta] * 0.5 / max_lever
#         min_diff = c_list[sta] * 0.5 / min_lever
#         std_max, std_min = max(c_list[sta:]), min(c_list[sta:])
#         xnum = c_list[sta:].index(std_max) + sta
#         nnum = c_list[sta:].index(std_min) + sta
#         max_vol = sum(v_list[min(xnum, nnum):max(xnum, nnum)+1])
#         le_diff = std_max - std_min
#         std_diff = le_diff / max_vol
#         std_vol = max_vol / le_diff
#         h_num, l_num = 0, 0
#         for std in range(sta,len(t_list)):
#             cal_max, cal_min = max(h_list[sta:std+1]), min(l_list[sta:std+1])
#             h_diff = cal_max - c_list[sta]
#             l_diff = c_list[sta] - cal_min
#             if(h_num == 0) and (max_diff >= h_diff >= min_diff): h_num = std
#             if(l_num == 0) and (max_diff >= l_diff >= min_diff): l_num = std
#             if(h_num != 0) and (l_num != 0): break
#             if(std == len(t_list)-1) and ((h_num != 0) or (l_num != 0)): break
#         if(h_num == 0) and (l_num == 0): continue
#         if(h_num != 0) and (l_num != 0):
#           if(h_num < l_num):
#             k_vol = sum(v_list[sta:h_num+1])
#             kk_diff = k_vol / h_diff
#             k_order = 44
#           else:
#             k_vol = sum(v_list[sta:l_num+1])
#             kk_diff = k_vol / l_diff
#             k_order = 33
#         if(h_num == 0):
#           k_vol = sum(v_list[sta:l_num+1])
#           kk_diff = k_vol / l_diff
#           k_order = 33
#         if(l_num == 0):
#           k_vol = sum(v_list[sta:h_num+1])
#           kk_diff = k_vol / h_diff
#           k_order = 44
#         k_per = round(kk_diff / std_vol * 100, 2)
#         print(sym_bol, itv, k_order,k_per,c_list[sta], c_list[0])

#         if(h_num != 0):
#           for h_std in range(h_num, len(t_list)):
#             if(l_list[h_std] <= c_list[sta]):
#               order_position = 11
#               break
#         if(order_position == 11):
#           fr_max = max(h_list[sta:h_std+1])
#           fr_num = h_list[sta:].index(fr_max) + sta
#           fr_vol = sum(v_list[sta:fr_num])
#           ba_vol = sum(v_list[fr_num:h_std+1])
#           fr_per = round(fr_vol / ba_vol * 100, 2)
#           cal_diff = fr_max - c_list[sta]
#           cal_lever = round(c_list[sta] * 0.5 / cal_diff, 2)
#           print(order_position,h_num,c_list[sta], c_list[0],fr_per,cal_lever)

#         if(l_num != 0):
#           for l_std in range(l_num, len(t_list)):
#             if(h_list[l_std] >= c_list[sta]):
#               order_position = 22
#               break
#         if(order_position == 22):
#           fr_max = min(l_list[sta:l_std+1])
#           fr_num = l_list[sta:].index(fr_max) + sta
#           fr_vol = sum(v_list[sta:fr_num])
#           ba_vol = sum(v_list[fr_num:l_std+1])
#           fr_per = round(fr_vol / ba_vol * 100, 2)
#           cal_diff = abs(fr_max - c_list[sta])
#           cal_lever = round(c_list[sta] * 0.5 / cal_diff, 2)
#           print(order_position,l_num,c_list[sta], c_list[0],fr_per,cal_lever)
#         if(order_position == 9): continue
# #          if(min(abs(std_max - c_list[0]), abs(std_min - c_list[0]))>=max_diff): continue

#         break
#     #-------------------------------------------------------------------------------
#       #print(sym_bol, itv, order_position)
#       order_return = [order_position]
#       return(order_return)
# for sym_bol in added_symbols[:30]:
#   order_return = search_calc(sym_bol)

