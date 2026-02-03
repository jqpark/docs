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

MAIN_JQ = "7889824708:AAGxaMmMwoBqYfK0Uoo6x5yml_xlnNhcHoo"
JQPARK = "6317837892:AAEQkXFTEJFLnvXgRZzulpzY_1pYjhR-fxM"
SMA000 = "5167779817:AAG8yAxw6mcWitb0NLi_KN4ms2vv9vDuqQA"
SMA020 = "5550859753:AAFGOcHoT_NK04x3ZnEu_WhzinAqxXUIrlU"
chat_id = 5372863028

order_id = MAIN_JQ

#MAIN_JQ
if(order_id == MAIN_JQ):
  session = HTTP(
    testnet=False,
    api_key="iPO6ATgyMtjsRIdUqq",
    api_secret="txYdie99Kn5XSEb0KjsJkOGItf5bRGvgHfkh",
    max_retries=10,
    retry_delay=15,
  )

#JQPARK
if(order_id == JQPARK):
  session = HTTP(
    testnet=False,
    api_key="LRkVDvSOR7uMQJ8Dsn",
    api_secret="lzzvrHvl9naF5YJE04M0H5CyzuYsRie8hh5g",
    max_retries=10,
    retry_delay=15,
  )

#SMA000
if(order_id == SMA000):
  session = HTTP(
    testnet=False,
    api_key="uv9MYvsNlh5f4XSXJU",
    api_secret="S4A3bZNZ5vfddXYQ2xjGXCFfmTHvKh0jSNhH",
    max_retries=10,
    retry_delay=15,
  )

#SMA020
if(order_id == SMA020):
  session = HTTP(
    testnet=False,
    api_key="EE0YCNPEGaVVfDvsCh",
    api_secret="SlmtbkKMfFrZumag5ceTXRYA4wWZS55pc2eZ",
    max_retries=10,
    retry_delay=15,
  )

invest_usdt = 2
delay_time = 60 #time_itv*60
check_time = 0
check_time1 = 0
return_time = 10
print_time = 100
tickers = session.get_tickers(category="linear")['result']['list']
symbol_list = (pd.DataFrame(tickers)['symbol'])
turnover_list = (pd.DataFrame(tickers)['turnover24h']).astype(float)
price_list = (pd.DataFrame(tickers)['lastPrice']).astype(float)
diff_list = (pd.DataFrame(tickers)['price24hPcnt']).astype(float)  
values = pd.concat([symbol_list,turnover_list,price_list,diff_list],axis=1)
sort_list = values.sort_values('price24hPcnt',key=lambda x: x.abs(),ignore_index=True,ascending=False)
added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e+07)]
added_symbols = added_list["symbol"].tolist()

open_list = []
item_list = pd.DataFrame(session.get_open_orders(category="linear",settleCoin="USDT",orderFilter='StopOrder',limit=50)['result']['list'])
if item_list.empty: open_list = []
else:
  open_list = item_list['symbol'].unique().tolist()
#added_symbols = open_list
#added_list = pd.DataFrame(session.get_closed_pnl(category="linear",limit=100)['result']['list'])
#added_symbols = added_list["symbol"].unique().tolist()
first_time = int(time.time())
first_server_time = str(datetime.utcfromtimestamp(first_time) + timedelta(hours=9))
print(first_server_time,len(added_symbols))

itv = 3
#-------------------------------------------------------------------------------
itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]
#-------------------------------------------------------------------------------
for sym in range(len(added_symbols)):
  sym_bol = added_symbols[sym]
  order_list =[]

  for itv in itv_list:

    get_kline=session.get_kline(category="linear",symbol=sym_bol,
              interval=str(itv),limit=1000)['result']['list']
#  time.sleep(1)
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
#--------------------------------------------------------------------------
    cal_lever, order_position = 0, 0
    cal_max, cal_min = 0, 0
    cal_upp, cal_low = 0, 0
    fr_vol, md_vol, bk_vol = 0, 0, 0
    upp_lever, low_lever = 0, 0
    std_diff = c_list[0] * 0.5 / 5
    limit_diff = std_diff
    upp_max, low_min = max(h_list), min(l_list)
    max_diff = upp_max - low_min
    xnum = h_list.index(upp_max)
    nnum = l_list.index(low_min)
    max_vol = sum(v_list[min(nnum,xnum):max(nnum,xnum)+1])
    max_avg = max_vol / max_diff

    diff_range = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
    for diff in diff_range:
      if(max_diff > std_diff):
          std_vol = max_avg * (std_diff * diff)

          for fr in range(1,len(c_list)):
            fr_vol = sum(v_list[:fr])
            if(fr_vol > std_vol):
              fr_max = max(h_list[:fr])
              fr_min = min(l_list[:fr])
              fr_xnum = h_list[:fr].index(fr_max)
              fr_nnum = l_list[:fr].index(fr_min)
              break
  #-------------------------------------------------------------------------------
          if(fr_vol <= std_vol): continue
  #-------------------------------------------------------------------------------     
          for md in range(fr,len(v_list)):
            md_vol = sum(v_list[fr:md])
            if(md_vol > std_vol):
              md_max = max(h_list[fr:md])
              md_min = min(l_list[fr:md])
              md_diff = md_max - md_min
              md_xnum = h_list[fr:md].index(md_max) + fr
              md_nnum = l_list[fr:md].index(md_min) + fr
              break
  #-------------------------------------------------------------------------------
          if(md_vol <= std_vol): continue
  #-------------------------------------------------------------------------------
          for bk in range(md,len(v_list)):
            bk_vol = sum(v_list[md:bk])
            if(bk_vol > std_vol):
              bk_max = max(h_list[md:bk])
              bk_min = min(l_list[md:bk])
              bk_diff = bk_max - bk_min
              bk_xnum = h_list[md:bk].index(bk_max) + md
              bk_nnum = l_list[md:bk].index(bk_min) + md
              break
  #-------------------------------------------------------------------------------
          if(bk_vol <= std_vol): continue
      else: continue
        
      if(min(fr_vol, md_vol, bk_vol) > std_vol): break    
  #-------------------------------------------------------------------------------
    if(min(fr_vol, md_vol, bk_vol) > std_vol):
          cal_max = min(fr_max, md_max, bk_max)
          cal_min = max(fr_min, md_min, bk_min)
          cal_upp = max(cal_max, cal_min)
          cal_low = min(cal_max, cal_min)

          if(cal_max < c_list[0]) and (c_list[0] > cal_min):
            order_position = 10
            upp_diff = max(fr_max, md_max, bk_max) - c_list[0]
            low_diff = c_list[0] - min(fr_min, md_min, bk_min)

          elif(cal_max > c_list[0]) and (c_list[0] < cal_min):
            order_position = 20
            upp_diff = max(fr_max, md_max, bk_max) - c_list[0]
            low_diff = c_list[0] - min(fr_min, md_min, bk_min)

          else: 
            order_position = 3
            upp_diff = max(fr_max, md_max, bk_max) - cal_low
            low_diff = cal_upp - min(fr_min, md_min, bk_min)
#          upp_diff = max(fr_max, md_max, bk_max) - c_list[0]
#          low_diff = c_list[0] - min(fr_min, md_min, bk_min)
          cal_diff = abs(cal_max - cal_min)
          if(upp_diff == 0): upp_lever = 100
          else: upp_lever = round(c_list[0] * 0.5 / upp_diff,2)
          if(low_diff == 0): low_lever = 100  
          else: low_lever = round(c_list[0] * 0.5 / low_diff,2)
          if(cal_diff == 0): cal_lever = 100
          else: cal_lever = round(c_list[0] * 0.5 / cal_diff,2)

          if(cal_max >= cal_upp) and (cal_min <= cal_low):
            if(order_position == 10): order_position = 11
            if(order_position == 20): order_position = 22
            if(order_position == 3): order_position = 33

          l_selection, s_selection = 0, 0
          if(low_lever <= 10) and (low_lever >= 5): l_selection = 1
          if(upp_lever <= 10) and (upp_lever >= 5): s_selection = 2
          if(order_position == 11) and (l_selection == 1): order_position = 1
          if(order_position == 22) and (s_selection == 2): order_position = 2  

          if(order_position == 33) and (l_selection == 1) and (s_selection == 2): order_position = 3
          elif(order_position == 33) and (l_selection == 1): order_position = 31
          elif(order_position == 33) and (s_selection == 2): order_position = 32
          print(itv, diff, sym_bol, order_position, upp_lever, low_lever)
          break
