#Replit
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
print(added_symbols1[:30])
print(added_symbols3[:30])
print(added_symbols2[:30])
added_symbols = added_symbols1.copy()
sort_list = df.sort_values('price24hPcnt', key=lambda x: x.abs(), ascending=False, ignore_index=True)
sort_symbols = sort_list["symbol"].tolist()
print(len(sort_symbols))
added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
added_symbols1 = added_list["symbol"].tolist()
added_symbols2 = added_list["price24hPcnt"].tolist()
added_symbols3 = added_list["turnover24h"].tolist()
print(added_symbols1[:30])
print(added_symbols3[:30])
print(added_symbols2[:30])
#added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e7)]
#  added_list = sort_list[(sort_list['lastPrice'] > 0.01) & (sort_list['lastPrice'] < 2) & (sort_list['turnover24h'] > 3e+07)]
#  added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
#added_symbols = added_list["symbol"].tolist()
#print(added_symbols)
##############################################################################
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
    max_lever, min_lever, cal_lever = 5, 10, 99
    max_diff = c_list[0] * 0.5 / max_lever
    min_diff = c_list[0] * 0.5 / min_lever
    std_max, std_min = max(h_list), min(l_list)
    if(max_diff > max(abs(std_max - c_list[0]), abs(std_min - c_list[0]))): continue
    xnum = h_list.index(std_max)
    nnum = l_list.index(std_min)
    max_vol = sum(v_list[min(xnum, nnum):max(xnum, nnum)+1])
    max_pol = sum(p_list[min(xnum, nnum):max(xnum, nnum)+1])
    std_diff = std_max - std_min
    limit_diff = std_diff
    std_vol = max_vol / std_diff
    std_pol = max_pol / std_diff
    h_num, l_num = 0, 0
    vol_per, pol_per = 99, 99
    std_list, vol_list, pol_list = [], [], []
    for std in range(len(t_list)):
        h_diff = h_list[std] - c_list[0]
        l_diff = c_list[0] - l_list[std]
        if(h_diff >= min_diff):
            order_position = 22
            break
        if(l_diff >= min_diff):    
            order_position = 11
            break
    if(order_position == 22):
      for h_d in range(std,len(t_list)):
          h_diff = h_list[l_d] - c_list[0]
          if(h_diff >= max_diff) or (h_diff < 0): break
          if(h_diff >= min_diff):
              cal_vol, cal_pol = sum(v_list[:h_d + 1]),       sum(p_list[:h_d + 1])
              vol_diff, pol_diff = cal_vol / h_diff,          cal_pol / h_diff
              vol_per, pol_per = vol_diff / std_vol * 100,    pol_diff / std_pol * 100
              std_list.append(std), vol_list.append(vol_per), pol_list.append(pol_per)
      std_list.reverse(), vol_list.reverse(), pol_list.reverse()
      for cal in range(len(std_list)):
          if(max(vol_list[cal], pol_list[cal]) < 50): break
      cal_num = std_list[cal]
      cal_max = h_list[cal_num]
      cal_min = min(l_list[:cal_num])
      cal_diff = cal_max - c_list[0]
      limit_diff = cal_diff
      cal_lever = round(c_list[0] * 0.5 / limit_diff, 2)
      xnum = h_list.index(cal_max)
      nnum = l_list.index(cal_min)
          
    if(order_position == 11):
      for l_d in range(std,len(t_list)):
          l_diff = c_list[0] - l_list[l_d]
          if(l_diff >= max_diff) or (l_diff < 0): break
          if(l_diff >= min_diff):
              cal_vol, cal_pol = sum(v_list[:l_d + 1]),       sum(p_list[:l_d + 1])
              vol_diff, pol_diff = cal_vol / l_diff,          cal_pol / l_diff
              vol_per, pol_per = vol_diff / std_vol * 100,    pol_diff / std_pol * 100
              std_list.append(std), vol_list.append(vol_per), pol_list.append(pol_per)
      std_list.reverse(), vol_list.reverse(), pol_list.reverse()
      for cal in range(len(std_list)):
          if(max(vol_list[cal], pol_list[cal]) < 50): break
      cal_num = std_list[cal]
      cal_min = l_list[cal_num]
      cal_max = max(h_list[:cal_num])
      cal_diff = c_list[0] - cal_min
      limit_diff = cal_diff
      cal_lever = round(c_list[0] * 0.5 / limit_diff, 2)
      xnum = h_list.index(cal_max)
      nnum = l_list.index(cal_min)
            
    if(max(vol_list[cal], pol_list[cal]) < 50) and (max_lever <= cal_lever <= min_lever):
      if(order_position == 11): order_position = 1
      if(order_position == 22): order_position = 2
    break
#-------------------------------------------------------------------------------
  print(sym_bol, itv, order_position,round(vol_list[cal],2),round(pol_list[cal],2))
  print(cal_lever,cal_max, cal_min)
  print(std_list)
  order_return = [order_position]
  return(order_return)
for sym_bol in added_symbols[:30]:
  order_return = search_calc(sym_bol)
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
  
