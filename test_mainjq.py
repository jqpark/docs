#v5_test15-3-2_MAIN_JQ_260119-1730
#v5 api
#Optimization <- v5_test13-6-3_SMA020_250619-1700
#telegram update using nest_asyncio
#pip install pybit==5.5.0
#pip install python-telegram-bot --upgrade
#pip install nest_asyncio
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

#wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
#my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
#live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
#tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
#avail_usdt = my_usdt - tot_position

#max_l_usdt, min_l_usdt, origin_usdt = live_usdt, live_usdt, my_usdt
#max_m_usdt, min_m_usdt = my_usdt, my_usdt
#max_t_position = tot_position

invest_usdt = 2
delay_time = 60 #time_itv*60
check_time = 0
check_time1 = 0
return_time = 10
print_time = 300
first_time = int(time.time())
###############################################################################
##############################################################################
def order_market_part(add_order):
#   if(calc_result[0] == 0):
      print(session.place_order(   # 주문하기.
               category="linear",
               symbol=add_order[0],   # 주문할 코인
               side=add_order[1],   # long주문
               orderType='Market', #'Limit',   # 시장가.
               qty=add_order[2],   # 개수
               timeInForce="GTC",
               positionIdx=add_order[3],        #hedge-mode Buy side
               takeProfit=add_order[4],
               stopLoss=add_order[5],
               reduceOnly=False,
               closeOnTrigger=False,
             ))

      time.sleep(1)
##############################################################################
def order_limit_part(add_order):
#   if(calc_result[0] == 0):
      print(session.place_order(   # 주문하기.
               category="linear",
               symbol=add_order[0],   # 주문할 코인
               side=add_order[1],   # long주문
               orderType='Limit', #'Limit',   # 시장가.
               qty=add_order[2],   # 개수
               price=add_order[3],
#               triggerDirection=1,
#               triggerPrice=add_order[2],
               timeInForce="GTC",
               positionIdx=add_order[4],        #hedge-mode Buy side
               takeProfit=add_order[5],
               stopLoss=add_order[6],
               reduceOnly=False,
               closeOnTrigger=False,
             ))

      time.sleep(1)
##############################################################################
#symbol, side, qty, triggerdirection, triggerprice, position, stoploss
def conditional_market_part(add_order):
#   if(calc_result[0] == 0):
      print(session.place_order(   # 주문하기.
               category="linear",
               symbol=add_order[0],   # 주문할 코인
               side=add_order[1],   # long주문
               orderType='Market', #'Limit',   # 시장가.
               qty=add_order[2],   # 개수
               triggerDirection=add_order[3],
               triggerPrice=add_order[4],
               timeInForce="GTC",
               positionIdx=add_order[5],        #hedge-mode Buy side
               takeProfit=add_order[6],
               stopLoss=add_order[7],
               reduceOnly=False,
               closeOnTrigger=False,
             ))

      time.sleep(1)
##############################################################################
def closed_order_part(add_order):
    res_ponse=session.get_positions(category="linear",symbol=add_order[0])['result']['list']
    position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
    if(position_idx == 1):
      long_qty = pd.DataFrame(res_ponse)['size'][0]
      short_qty = pd.DataFrame(res_ponse)['size'][1]
    else:
      long_qty = pd.DataFrame(res_ponse)['size'][1]
      short_qty = pd.DataFrame(res_ponse)['size'][0]
#-------------------------------------------------------------------------------
#closed order condition
    if(add_order[2] == 1): closed_qty = str(long_qty)
    if(add_order[2] == 2): closed_qty = str(short_qty)
#-------------------------------------------------------------------------------
#closed order
    print(session.place_order(   # 주문하기.
               category="linear",
               symbol=add_order[0],   # 주문할 코인
               side=add_order[1],   # 청산주문
               orderType='Market', #'Limit',   # 시장가.
               qty=closed_qty,   # 개수
               timeInForce="GTC",
               positionIdx=add_order[2],        #hedge-mode Buy side
               reduceOnly=True,
               closeOnTrigger=True,
             ))

    time.sleep(1)
##############################################################################
##############################################################################
def set_stop_loss_item(add_order):
      print(session.set_trading_stop(
            category="linear",
            symbol=add_order[0],
            stopLoss=add_order[1],
            tpslMode="Full",
            positionIdx=add_order[2],
))
##############################################################################
##############################################################################
def set_trading_stop_item(add_order):
      print(session.set_trading_stop(
            category="linear",
            symbol=add_order[0],
            takeProfit="0",
            trailingStop=add_order[1],
            activePrice=add_order[2],
            tpslMode="Full",
            positionIdx=add_order[3],
))
################################################################################
################################################################################
def search_calc(sym_bol):
  itv_list = [3, 5 ,10, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]
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
    cal_lever, order_position = 0, 0
    std_diff = c_list[0] * 0.5 / 5
    limit_diff = std_diff
    for fr in range(1,len(c_list)):
      fr_max = max(h_list[:fr])
      fr_min = min(l_list[:fr])
      fr_diff = fr_max - fr_min
      if(fr_diff > std_diff): break
    fr_xnum = h_list[:fr].index(fr_max)
    fr_nnum = l_list[:fr].index(fr_min)
    fr_vol = sum(v_list[1:fr])
    for bk in range(fr,len(v_list)):
      bk_vol = sum(v_list[fr:bk])
      if(bk_vol > fr_vol): break
    if(fr != bk):
      bk_max = max(h_list[fr:bk])
      bk_min = min(l_list[fr:bk])
      bk_diff = bk_max - bk_min
      bk_xnum = h_list[fr:bk].index(bk_max) + fr
      bk_nnum = l_list[fr:bk].index(bk_min) + fr
    else:
      bk_vol = sum(v_list)
      bk_max = max(h_list)
      bk_min = min(l_list)
      bk_diff = bk_max - bk_min
      bk_xnum = h_list.index(bk_max)
      bk_nnum = l_list.index(bk_min)
    if(bk_vol > fr_vol): break
    else: time.sleep(1) 

  if(bk_max < fr_max) and (bk_min <= fr_min):
    limit_diff = abs(c_list[0] - bk_min)
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    if(abs(bk_max - fr_max) > abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 1
      if(cal_lever < 5): order_position = 11
      if(cal_lever > 10): order_position = 10
    if(abs(bk_max - fr_max) < abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 3
      if(cal_lever < 5): order_position = 31
      if(cal_lever > 10): order_position = 30
  if(bk_max >= fr_max) and (bk_min > fr_min):
    limit_diff = abs(bk_max - c_list[0])
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    if(abs(bk_max - fr_max) < abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 2
      if(cal_lever < 5): order_position = 21
      if(cal_lever > 10): order_position = 20
    if(abs(bk_max - fr_max) > abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 4
      if(cal_lever < 5): order_position = 41
      if(cal_lever > 10): order_position = 40
  if(bk_max >= fr_max) and (bk_min <= fr_min):
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    order_position = 91
  if(bk_max <= fr_max) and (bk_min >= fr_min):
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    order_position = 90

  print(sym_bol, order_position, cal_lever)
#-------------------------------------------------------------------------------
  time.sleep(1)
  return(order_position)
#-------------------------------------------------------------------------------
###############################################################################
################################################################################
#        order_value = [sym_bol, sym_price, order_condition[item_no], limit_diff_p[item_no],
#                       value_s_list[item_no], value_v_list[item_no]]
def order_calc(order_value):
  sym_bol = order_value[0]
  sym_price = order_value[1]
  open_order_condition = order_value[2]
  limit_diff = order_value[3]
  s_value_list = order_value[4]
  v_value_list = order_value[5]
#  itv = 3
  itv_list = [3, 5 ,10, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]
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
    cal_lever, order_position = 0, 0
    std_diff = c_list[0] * 0.5 / 5
    limit_diff = std_diff
    for fr in range(1,len(c_list)):
      fr_max = max(h_list[:fr])
      fr_min = min(l_list[:fr])
      fr_diff = fr_max - fr_min
      if(fr_diff > std_diff): break
    fr_xnum = h_list[:fr].index(fr_max)
    fr_nnum = l_list[:fr].index(fr_min)
    fr_vol = sum(v_list[1:fr])
    for bk in range(fr,len(v_list)):
      bk_vol = sum(v_list[fr:bk])
      if(bk_vol > fr_vol): break
    if(fr != bk):
      bk_max = max(h_list[fr:bk])
      bk_min = min(l_list[fr:bk])
      bk_diff = bk_max - bk_min
      bk_xnum = h_list[fr:bk].index(bk_max) + fr
      bk_nnum = l_list[fr:bk].index(bk_min) + fr
    else:
      bk_vol = sum(v_list)
      bk_max = max(h_list)
      bk_min = min(l_list)
      bk_diff = bk_max - bk_min
      bk_xnum = h_list.index(bk_max)
      bk_nnum = l_list.index(bk_min)
    if(bk_vol > fr_vol): break
    else: time.sleep(1) 

  if(bk_max < fr_max) and (bk_min <= fr_min):
    limit_diff = abs(c_list[0] - bk_min)
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    if(abs(bk_max - fr_max) > abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 1
      if(cal_lever < 5): order_position = 11
      if(cal_lever > 10): order_position = 10
    if(abs(bk_max - fr_max) < abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 3
      if(cal_lever < 5): order_position = 31
      if(cal_lever > 10): order_position = 30
  if(bk_max >= fr_max) and (bk_min > fr_min):
    limit_diff = abs(bk_max - c_list[0])
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    if(abs(bk_max - fr_max) < abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 2
      if(cal_lever < 5): order_position = 21
      if(cal_lever > 10): order_position = 20
    if(abs(bk_max - fr_max) > abs(bk_min - fr_min)):
      if(5 <= cal_lever <= 10): order_position = 4
      if(cal_lever < 5): order_position = 41
      if(cal_lever > 10): order_position = 40
  if(bk_max >= fr_max) and (bk_min <= fr_min):
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    order_position = 91
  if(bk_max <= fr_max) and (bk_min >= fr_min):
    cal_lever = round(c_list[0] * 0.5 / limit_diff,2)
    order_position = 90
  
  if(fr_max > bk_max): ord_max, ord_xnum = fr_max, fr_xnum
  else: ord_max, ord_xnum = bk_max, bk_xnum
  if(fr_min < bk_min): ord_min, ord_nnum = fr_min, fr_nnum
  else: ord_min, ord_nnum = bk_min, bk_nnum
  mx_time = float(t_list[ord_xnum] * 0.001)
  mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
  mn_time = float(t_list[ord_nnum] * 0.001)
  mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
  s_value_list = [order_position, ord_max, ord_min, cal_lever]
  v_value_list = [mx_server_time, mn_server_time]
#-------------------------------------------------------------------------------
  time.sleep(1)
  order_return = [open_order_condition, limit_diff, s_value_list, v_value_list]
  return(order_return)
#-------------------------------------------------------------------------------
###############################################################################
def calc_part(order_condition, sym_bol, h_price, l_price, lever_diff):
    instruments_info = session.get_instruments_info(category="linear",symbol=sym_bol)['result']['list']
#    time.sleep(1)
    qty_step = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['qtyStep']
    min_value = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minNotionalValue']
    min_qty = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minOrderQty']
    tick_size = pd.DataFrame(instruments_info)['priceFilter'][0]['tickSize']
    max_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['maxLeverage']
    min_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['minLeverage']
    lever_step = pd.DataFrame(instruments_info)['leverageFilter'][0]['leverageStep']

    risk_limit = session.get_risk_limit(category="linear",symbol=sym_bol)['result']['list']
    mm_rate = float(pd.DataFrame(risk_limit)['maintenanceMargin'][0])
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#pl leverage
#Liq_price = ent price x (1 + (1 / pl) - mm_rate)
    lever_point = h_price - lever_diff
    pl = float(min_lever)
    while True:
        liq_l_p = h_price * (1 - (1 / pl) + mm_rate)
        liq_l_limit = lever_point - abs((h_price - lever_point) * 0.1)
        liq_l_max = lever_point - abs((h_price - lever_point) * 0.1)
        max_l_perc = abs(h_price - (h_price * 0.5 / pl))
        if ((liq_l_p < liq_l_limit) and (max_l_perc < lever_point) and (pl < float(max_lever))):
            pl = pl + float(lever_step)
        else:
#            el_new_lever = str(pl - float(lever_step))
            el_new_lever = str(pl)
            if(float(el_new_lever) <= float(min_lever)): el_new_lever = min_lever
            l_new_lever = str(int(Decimal(el_new_lever) / Decimal(lever_step)) * Decimal(lever_step))
            if(float(l_new_lever) == 1): l_new_lever = str(1)
            break
#-------------------------------------------------------------------------------
#ps leverage
#Liq_price = ent price x (1 + (1 / ps) - mm_rate)
    lever_point = l_price + lever_diff
    ps = float(min_lever)
    while True:
        liq_s_p = l_price * (1 + (1 / ps) - mm_rate)
        liq_s_limit = lever_point + abs((l_price - lever_point) * 0.1)
        liq_s_max = lever_point + abs((l_price - lever_point) * 0.1)
        max_s_perc = abs(l_price + (l_price * 0.5 / ps))

        if ((liq_s_p > liq_s_limit) and (max_s_perc > lever_point) and (ps < float(max_lever))):
            ps = ps + float(lever_step)
        else:
#            es_new_lever = str(ps - float(lever_step))
            es_new_lever = str(ps)
            if(float(es_new_lever) <= float(min_lever)): es_new_lever = min_lever
            s_new_lever = str(int(Decimal(es_new_lever) / Decimal(lever_step)) * Decimal(lever_step))
            if(float(s_new_lever) == 1): s_new_lever = str(1)
            break
#-------------------------------------------------------------------------------
    if(float(l_new_lever) > 10): l_new_lever = "10"
    if(float(s_new_lever) > 10): s_new_lever = "10"
###############################################################################
    calc_return = [sym_bol, l_new_lever, s_new_lever]
    return(calc_return)
###############################################################################
###############################################################################
# make rest_item list
while True:
  wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
  my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
  live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
  tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
  avail_usdt = my_usdt - tot_position

  max_l_usdt, min_l_usdt, origin_usdt = live_usdt, live_usdt, my_usdt
  max_m_usdt, min_m_usdt = my_usdt, my_usdt
  max_t_position = tot_position

  try_item = []
#  if(avail_usdt < (invest_usdt * 2)):
#    item_list = session.get_open_orders(category="linear",settleCoin="USDT")['result']['list']
#    if(item_list == []): rest_item = []
#    else: rest_item = pd.DataFrame(item_list)['symbol']
#    for i in range(len(rest_item)):
#      if(rest_item[i] in try_item): pass
#      else: try_item.append(rest_item[i])

  rest_list, open_list, trail_list, stop_list = [], [], [], []
  item_list = pd.DataFrame(session.get_open_orders(category="linear",settleCoin="USDT",orderFilter='StopOrder',limit=50)['result']['list'])
  if item_list.empty: open_list, trail_list, stop_list = [], [], []
  else:
    open_list = item_list['symbol'].unique().tolist()
    trail_list = item_list[(item_list['stopOrderType'] == 'TrailingStop')]
    trail_list = trail_list['symbol'].unique().tolist()
    stop_list = item_list[(item_list['stopOrderType'] == 'Stop')]
    stop_list = stop_list['symbol'].unique().tolist()
#    check_condition = lambda x: {1, 2}.issubset(set(x))
#    double_list = item_list[item_list.groupby('symbol')['positionIdx'].transform(check_condition)]
#    except_list = list(set(pd.concat([Trail_list,double_list],axis=0)["symbol"].tolist()))
#  set_except = set(except_list)
  rest_list = [item for item in open_list if item not in trail_list]

#  get_positions = session.get_positions(category="linear",settleCoin="USDT")['result']['list']
#  if(get_positions == []): get_item, get_list = [], []
#  else: 
#    get_item = pd.DataFrame(get_positions)['symbol']
#    get_list = get_item.tolist()

  del_list = session.get_announcement(locale="en-US",type='Delistings',tag='Derivatives')['result']['list']
  if(del_list == []): title_list = []
  else: title_list = [item['title'] for item in del_list]
  all_words = []
  for title in title_list:
    all_words.extend(re.findall(r'\b\w+\b', title)) 
  uppercase_words = {word for word in all_words if word.isupper()}
  final_del_list = sorted(uppercase_words)

  cancel_list = []
  for sym_bol in trail_list:
    if sym_bol in stop_list: cancel_list.append(sym_bol)
  if(cancel_list != []):
    for sym_bol in cancel_list:
      session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')

  for i in range(len(rest_list)):
      try_item.append(rest_list[i])

  
#rest_item = try_item.copy()
#-------------------------------------------------------------------------------
#  first_time = int(time.time())
#-------------------------------------------------------------------------------
# add item list
  ordered_item = 10
  #wish_item_no = 15
  wish_item_no = 10
  if(wish_item_no > len(try_item)):
    tickers = session.get_tickers(category="linear")['result']['list']
    symbol_list = (pd.DataFrame(tickers)['symbol'])
    turnover_list = (pd.DataFrame(tickers)['turnover24h']).astype(float)
    price_list = (pd.DataFrame(tickers)['lastPrice']).astype(float)
    diff_list = (pd.DataFrame(tickers)['price24hPcnt']).astype(float)  
    values = pd.concat([symbol_list,turnover_list,price_list,diff_list],axis=1)
    sort_list = values.sort_values('price24hPcnt',key=lambda x: x.abs(),ignore_index=True,ascending=False)
#  added_list = sort_list[(sort_list['lastPrice'] > 0.01) & (sort_list['lastPrice'] < 2) & (sort_list['turnover24h'] > 3e+07)]
    added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e+07)]
#    added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
    added_symbols = added_list["symbol"].tolist()
    added_symbols = [x for x in added_symbols if x not in open_list]
    added_symbols = [x for x in added_symbols if x not in final_del_list]
    added_symbols = [x for x in added_symbols if 'USDT' in x]
#-------------------------------------------------------------------------------
    for sym_bol in added_symbols:
#      if(len(try_item) >= wish_item_no): break
      search_calc_result = search_calc(sym_bol)
      if(search_calc_result in (1, 2)): try_item.append(sym_bol)
#-------------------------------------------------------------------------------    
#    for i in range(len(added_symbols)):
#      if(len(try_item) >= wish_item_no): break
#      try_item.append(added_symbols[i])
#-------------------------------------------------------------------------------
#print(try_item)
#-------------------------------------------------------------------------------
  order_usdt, time_t, limit_diff_p = [], [], []
  max_margin, min_margin, max_pnl = [], [], []
  order_condition, pre_condition, value_s, value_s_list = [], [], [], []
  value_v, value_v_list, value_p, value_p_list = [], [], [], []
  half_condition, closed_order, wish_price, order_info = [], [], [], []

  i = 0
  while i < len(try_item):
    order_usdt.append(0), time_t.append(0), limit_diff_p.append(0)
    max_margin.append(0), min_margin.append(0), max_pnl.append(0)
    order_condition.append(0), pre_condition.append(0), value_s.append(0), value_s_list.append(0)
    value_v.append(0), value_v_list.append(0), value_p.append(0), value_p_list.append(0)
    half_condition.append(0), closed_order.append(0), wish_price.append(0), order_info.append(0)
    i = i + 1
#-------------------------------------------------------------------------------
  if(check_time1 == 0):
    btc_info=session.get_tickers(category="linear",symbol='BTCUSDT')['result']['list']
    btc_price = float(pd.DataFrame(btc_info)['lastPrice'][0])
    url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'order_id_Equity = ',round(live_usdt,2), 'My Wallet = ', round(my_usdt,2),'BTCUSDT = ',btc_price}"
#  url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'Test-JQ_BTCUSDT = ',btc_price}"
    requests.get(url).json() # this sends the message  max_usdt = live_usdt
    url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'new_item_list:',try_item}"
    requests.get(url).json() # this sends the message
  check_time1 = check_time1 + 1
###############################################################################
#  while True:
#-------------------------------------------------------------------------------
#    wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
##    time.sleep(1)
#    my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
#    live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
#    tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
#    avail_usdt = my_usdt - tot_position

#    if(max_l_usdt <= live_usdt): max_l_usdt = live_usdt
#    if(min_l_usdt >= live_usdt): min_l_usdt = live_usdt
#    if(max_m_usdt <= my_usdt): max_m_usdt = my_usdt
#    if(min_m_usdt >= my_usdt): min_m_usdt = my_usdt
#    if(max_t_position <= tot_position): max_t_position = tot_position

  if(try_item != []):  
    last_time = int(time.time())
###############################################################################
    for sym_bol in try_item:
      item_no = try_item.index(sym_bol)
      i_last_time = int(time.time())
      now_time = int(time.time()) * 1000
###############################################################################
      sym_info=session.get_tickers(category="linear",symbol=sym_bol)['result']['list']
#      time.sleep(1)
      sym_price = float(pd.DataFrame(sym_info)['lastPrice'][0])

      res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
#      time.sleep(1)
      position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
      if(position_idx == 1):
        long_qty = float(pd.DataFrame(res_ponse)['size'][0])
        short_qty = float(pd.DataFrame(res_ponse)['size'][1])
        l_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
        s_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
        l_ent_price = pd.DataFrame(res_ponse)['avgPrice'][0]
        s_ent_price = pd.DataFrame(res_ponse)['avgPrice'][1]
        l_unpnl = pd.DataFrame(res_ponse)['unrealisedPnl'][0]
        s_unpnl = pd.DataFrame(res_ponse)['unrealisedPnl'][1]
        l_position = pd.DataFrame(res_ponse)['positionBalance'][0]
        s_position = pd.DataFrame(res_ponse)['positionBalance'][1]
        l_st_loss = pd.DataFrame(res_ponse)['stopLoss'][0]
        if not l_st_loss.strip(): l_st_loss = 0
        s_st_loss = pd.DataFrame(res_ponse)['stopLoss'][1]
        if not s_st_loss.strip(): s_st_loss = 0
        l_trailing = pd.DataFrame(res_ponse)['trailingStop'][0]
        if not l_trailing.strip(): l_trailing = 0
        s_trailing = pd.DataFrame(res_ponse)['trailingStop'][1]
        if not s_trailing.strip(): s_trailing = 0
        l_trade_mode = pd.DataFrame(res_ponse)['tradeMode'][0]
        s_trade_mode = pd.DataFrame(res_ponse)['tradeMode'][1]
        l_position_im = pd.DataFrame(res_ponse)['positionIM'][0]
        if not l_position_im.strip(): l_position_im = 0
        s_position_im = pd.DataFrame(res_ponse)['positionIM'][1]
        if not s_position_im.strip(): s_position_im = 0
      else:
        long_qty = float(pd.DataFrame(res_ponse)['size'][1])
        short_qty = float(pd.DataFrame(res_ponse)['size'][0])
        l_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
        s_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
        l_ent_price = pd.DataFrame(res_ponse)['avgPrice'][1]
        s_ent_price = pd.DataFrame(res_ponse)['avgPrice'][0]
        l_unpnl = pd.DataFrame(res_ponse)['unrealisedPnl'][1]
        s_unpnl = pd.DataFrame(res_ponse)['unrealisedPnl'][0]
        l_position = pd.DataFrame(res_ponse)['positionBalance'][1]
        s_position = pd.DataFrame(res_ponse)['positionBalance'][0]
        l_st_loss = pd.DataFrame(res_ponse)['stopLoss'][1]
        if not l_st_loss.strip(): l_st_loss = 0
        s_st_loss = pd.DataFrame(res_ponse)['stopLoss'][0]
        if not s_st_loss.strip(): s_st_loss = 0
        l_trailing = pd.DataFrame(res_ponse)['trailingStop'][1]
        if not l_trailing.strip(): l_trailing = 0
        s_trailing = pd.DataFrame(res_ponse)['trailingStop'][0]
        if not s_trailing.strip(): s_trailing = 0
        l_trade_mode = pd.DataFrame(res_ponse)['tradeMode'][1]
        s_trade_mode = pd.DataFrame(res_ponse)['tradeMode'][0]
        l_position_im = pd.DataFrame(res_ponse)['positionIM'][1]
        if not l_position_im.strip(): l_position_im = 0
        s_position_im = pd.DataFrame(res_ponse)['positionIM'][0]
        if not s_position_im.strip(): s_position_im = 0

      instruments_info = session.get_instruments_info(category="linear",symbol=sym_bol)['result']['list']
#      time.sleep(1)
      qty_step = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['qtyStep']
      min_value = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minNotionalValue']
      min_qty = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minOrderQty']
      tick_size = pd.DataFrame(instruments_info)['priceFilter'][0]['tickSize']
      max_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['maxLeverage']
      min_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['minLeverage']
      lever_step = pd.DataFrame(instruments_info)['leverageFilter'][0]['leverageStep']
      status = instruments_info[0]['status']

      wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
#      time.sleep(1)
      my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
      avail_usdt = pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['availableToWithdraw'][0]
      live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
      tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
      if avail_usdt.strip(): avail_usdt = float(avail_usdt)
      else: avail_usdt = my_usdt - tot_position
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
      m_order_type_list = []
      m_order_idx, m_order_tp, m_order_st = [0, 0, 0], [0, 0, 0], [0, 0, 0]
      m_get_open=session.get_open_orders(category="linear",symbol=sym_bol,orderFilter='StopOrder')['result']['list']
#      time.sleep(1)
      m_stop_order_list = [(m_stop_order["positionIdx"],m_stop_order["triggerPrice"], m_stop_order["stopLoss"]) for m_stop_order in m_get_open if m_stop_order.get("stopOrderType") == "Stop"]
      if(m_stop_order_list != []):
        for list in range(len(m_stop_order_list)):
          if(m_stop_order_list[list][0] == 1):
            m_order_idx[1], m_order_tp[1], m_order_st[1] = m_stop_order_list[list][0], float(m_stop_order_list[list][1]), float(m_stop_order_list[list][2])
          if(m_stop_order_list[list][0] == 2):
            m_order_idx[2], m_order_tp[2], m_order_st[2] = m_stop_order_list[list][0], float(m_stop_order_list[list][1]), float(m_stop_order_list[list][2])
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
      if(try_item != []):  
#-------------------------------------------------------------------------------
#START
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# order_calc
        order_value = [sym_bol, sym_price, order_condition[item_no], limit_diff_p[item_no],
                       value_s_list[item_no], value_v_list[item_no]]
        order_calc_result = order_calc(order_value)
#-------------------------------------------------------------------------------
# order_calc_result
        order_condition[item_no] = order_calc_result[0]
        limit_diff_p[item_no] = order_calc_result[1]
        value_s_list[item_no] = order_calc_result[2]
        value_v_list[item_no] = order_calc_result[3]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        h_price, l_price = sym_price, sym_price
#-------------------------------------------------------------------------------
# calc_part_result
# calc_return = [sym_bol, l_new_lever, s_new_lever]
        calc_result = calc_part(order_condition[item_no], sym_bol, h_price, l_price, limit_diff_p[item_no])
#-------------------------------------------------------------------------------
        if(float(max_lever) >= max(float(calc_result[1]), float(calc_result[2]))) and (value_s_list[item_no][0] in (1, 2)):  
          if(long_qty == 0) and (short_qty == 0):
            if(float(calc_result[1]) != float(l_sym_lever)) or (float(calc_result[2]) != float(s_sym_lever)):
              session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=calc_result[1], sellLeverage=calc_result[2])
              time.sleep(1)
          if(long_qty == 0) and (short_qty != 0) and (float(calc_result[1]) != float(l_sym_lever)):
              session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=calc_result[1], sellLeverage=s_sym_lever)
              time.sleep(1)
          if(long_qty != 0) and (short_qty == 0) and (float(calc_result[2]) != float(s_sym_lever)):
              session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=l_sym_lever, sellLeverage=calc_result[2])
              time.sleep(1)

        res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
#        time.sleep(1)
        position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
        if(position_idx == 1):
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
        else:
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        l_ex_price = str(h_price + float(tick_size))
        l_order_price = str(int(Decimal(l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_ex_qty = str((invest_usdt * float(l_sym_lever)) / float(l_order_price))
        l_order_qty = str(int(Decimal(l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        l_tp_ex_price = str(h_price + (limit_diff_p[item_no] * 5) + float(tick_size))
        l_tp_price = str(int(Decimal(l_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_st_ex_price = str(h_price - limit_diff_p[item_no] - float(tick_size))
        l_st_price = str(int(Decimal(l_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_order_side = 'Buy'
        l_order_position = 1
        l_ex_value = float(l_order_qty) * float(l_order_price) * 1.0

        s_ex_price = str(l_price - float(tick_size))
        s_order_price = str(int(Decimal(s_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_ex_qty = str((invest_usdt * float(s_sym_lever)) / float(s_order_price))
        s_order_qty = str(int(Decimal(s_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        s_tp_ex_price = str(l_price - (limit_diff_p[item_no] * 5) - float(tick_size))
        s_tp_price = str(int(Decimal(s_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_st_ex_price = str(l_price + limit_diff_p[item_no] + float(tick_size))
        s_st_price = str(int(Decimal(s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_order_side = 'Sell'
        s_order_position = 2
        s_ex_value = float(s_order_qty) * float(s_order_price) * 1.0
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
#        time.sleep(1)
        position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
        if(position_idx == 1):
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
        else:
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(value_s_list[item_no][0] == 1) and (m_order_idx[1] == 1):
            if(m_order_tp[1] != float(l_order_price)):
              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')

        if(value_s_list[item_no][0] == 2) and (m_order_idx[2] == 2):
            if(m_order_tp[2] != float(s_order_price)):
              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------
        if(value_s_list[item_no][0] != 0) and (value_s_list[item_no][1] > sym_price > value_s_list[item_no][2]):
#-------------------------------------------------------------------------------
          if(value_s_list[item_no][0] == 1):
            if(long_qty == 0) and ((invest_usdt * 1) < avail_usdt) and (float(l_sym_lever) == float(calc_result[1])):
                if(float(max_lever) >= float(l_sym_lever)) and (m_order_idx[1] == 0):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_tp_price, l_st_price]
#                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, 1, l_tp_price, l_st_price]                  
                    order_market_part(add_order)
                    time.sleep(1)

          if(value_s_list[item_no][0] == 2):
            if(short_qty == 0) and ((invest_usdt * 1) < avail_usdt) and (float(s_sym_lever) == float(calc_result[2])):
                if(float(max_lever) >= float(s_sym_lever)) and (m_order_idx[2] == 0):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_tp_price, s_st_price]                  
#                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    order_market_part(add_order)
                    time.sleep(1)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#        if(long_qty != 0):
#          ex_act_price = str(float(l_ent_price) + (abs(float(l_ent_price) - float(l_st_loss))))
#          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
#          if(float(l_trailing) == 0) and (float(act_price) > sym_price):
#            ex_ts_diff = abs(float(l_ent_price) - float(l_st_loss)) * 1.0
#            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
#            add_order = [sym_bol, ts_diff, act_price, 1]
#            set_trading_stop_item(add_order)
#-------------------------------------------------------------------------------
#        if(short_qty != 0):
#          ex_act_price = str(float(s_ent_price) - (abs(float(s_ent_price) - float(s_st_loss))))
#          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
#          if(float(s_trailing) == 0) and (float(act_price) < sym_price):
#            ex_ts_diff = abs(float(s_ent_price) - float(s_st_loss)) * 1.0
#            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
#            add_order = [sym_bol, ts_diff, act_price, 2]
#            set_trading_stop_item(add_order)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(long_qty != 0):
          if(value_s_list[item_no][0] in (2, 21, 4, 41)):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'L_closed'
            opened_order_info = [sym_bol, order_condition[item_no], round(float(l_unpnl),2), value_s_list[item_no]]
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message

        if(short_qty != 0):
          if(value_s_list[item_no][0] in (1, 11, 3, 31)):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'S_closed'
            opened_order_info = [sym_bol, order_condition[item_no], round(float(s_unpnl),2), value_s_list[item_no]]
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message
#-------------------------------------------------------------------------------
        if(long_qty != 0):
          if(value_s_list[item_no][0] == 91) and (float(l_unpnl) > (invest_usdt * 0.1)):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'PF_L_closed'
            opened_order_info = [sym_bol, order_condition[item_no], round(float(l_unpnl),2), value_s_list[item_no]]
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message

        if(short_qty != 0):
          if(value_s_list[item_no][0] == 91) and (float(s_unpnl) > (invest_usdt * 0.1)):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'PF_S_closed'
            opened_order_info = [sym_bol, order_condition[item_no], round(float(s_unpnl),2), value_s_list[item_no]]
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message
#-------------------------------------------------------------------------------
        if(long_qty != 0):
          if(float(l_position_im) > (invest_usdt * 1.5)):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'Over_order_L_closed'
            opened_order_info = [sym_bol, pre_condition[item_no], order_condition[item_no], round(float(l_position_im),1)]
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message

        if(short_qty != 0):
          if(float(s_position_im) > (invest_usdt * 1.5)):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'Over_order_S_closed'
            opened_order_info = [sym_bol, pre_condition[item_no], order_condition[item_no], round(float(s_position_im),1)]
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message
###############################################################################
        if (long_qty != 0):
          print(sym_bol,sym_price,'order_condition:',order_condition[item_no],'now_m:',l_unpnl)
        elif (short_qty != 0):
          print(sym_bol,sym_price,'order_condition:',order_condition[item_no],'now_m:',s_unpnl)
        else:
          print(sym_bol,sym_price,order_condition[item_no], 'PASS')
        print('lever_ex_value:',calc_result[1], calc_result[2])
        print('value_s:',value_s_list[item_no])
        print('value_v:',value_v_list[item_no])
###############################################################################
        i_this_time = int(time.time())
        i_diff_time = i_this_time - i_last_time
        i_rest_time = int(6 - i_diff_time)
#        if(i_rest_time > 0): time.sleep(i_rest_time)
###############################################################################
    this_time = int(time.time())
    diff_time = this_time - last_time
    rest_time = int(60 - diff_time)
#    if(rest_time > 0): time.sleep(rest_time)
#    check_time = check_time + 1
#    check_time1 = check_time1 + 1
    if(check_time1 >= print_time):
      run_time = int(time.time())
      one_cycle = round((run_time - first_time) / (60 * 60),1)
      first_time = int(time.time())
      url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'one_cycle(hr):',one_cycle}"
      requests.get(url).json() # this sends the message
      check_time1 = 0
#    if(check_time >= return_time):
#      check_time = 0
#      break
###############################################################################
    korea_tz = pytz.timezone('Asia/Seoul')
    current_time_korea = datetime.now(korea_tz)
    current_time = current_time_korea.strftime('%Y-%m-%d %H:%M:%S')
    print('l_USDT_MAX_MIN :',round(max_l_usdt,2),round(min_l_usdt,2),'live_USDT: ',round(live_usdt,2))
    print('m_USDT_MAX_MIN :',round(max_m_usdt,2),round(min_m_usdt,2),'my_USDT: ',round(my_usdt,2),'origin_usdt:',round(origin_usdt,2))
    print('T_POSITION_MAX_NOW :',round(max_t_position,2),round(tot_position,2),'invest_USDT:',round(invest_usdt,1))
    print(current_time,'check_time =',check_time,'Reset')
