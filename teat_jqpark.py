#v5_test14-9-4_JQPARK_251014-1630
#v5 api
#Optimization <- v5_test13-6-3_SMA020_250619-1700
#problume -> v5_test13-6-2_JQPARK_250523-1620 - retry code
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

#MAIN_JQ
#MAIN_JQ = "7889824708:AAGxaMmMwoBqYfK0Uoo6x5yml_xlnNhcHoo"
#JQPARK
JQPARK = "6317837892:AAEQkXFTEJFLnvXgRZzulpzY_1pYjhR-fxM"
#SMA000
#SMA000 = "5167779817:AAG8yAxw6mcWitb0NLi_KN4ms2vv9vDuqQA"
#SMA020
#SMA020 = "5550859753:AAFGOcHoT_NK04x3ZnEu_WhzinAqxXUIrlU"
chat_id = 5372863028

#MAIN_JQ
#session = HTTP(
#    testnet=False,
#    api_key="iPO6ATgyMtjsRIdUqq",
#    api_secret="txYdie99Kn5XSEb0KjsJkOGItf5bRGvgHfkh",
#    max_retries=10,
#    retry_delay=15,
#)

#JQPARK
session = HTTP(
    testnet=False,
    api_key="LRkVDvSOR7uMQJ8Dsn",
    api_secret="lzzvrHvl9naF5YJE04M0H5CyzuYsRie8hh5g",
    max_retries=10,
    retry_delay=15,
)

#SMA000
#session = HTTP(
#    testnet=False,
#    api_key="uv9MYvsNlh5f4XSXJU",
#    api_secret="S4A3bZNZ5vfddXYQ2xjGXCFfmTHvKh0jSNhH",
#    max_retries=10,
#    retry_delay=15,
#)

#SMA020
#session = HTTP(
#    testnet=False,
#    api_key="EE0YCNPEGaVVfDvsCh",
#    api_secret="SlmtbkKMfFrZumag5ceTXRYA4wWZS55pc2eZ",
#    max_retries=10,
#    retry_delay=15,
#)

order_id = JQPARK

wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
avail_usdt = my_usdt - tot_position

max_l_usdt, min_l_usdt, origin_usdt = live_usdt, live_usdt, my_usdt
max_m_usdt, min_m_usdt = my_usdt, my_usdt
max_t_position = tot_position

invest_usdt = 2
delay_time = 60 #time_itv*60
check_time = 0
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
#               takeProfit=add_order[18],
               stopLoss=add_order[4],
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
#               takeProfit=calc_result[18],
               stopLoss=add_order[5],
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
#               takeProfit=calc_result[18],
               stopLoss=add_order[6],
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
            trailingStop=add_order[1],
            activePrice=add_order[2],
            tpslMode="Full",
            positionIdx=add_order[3],
))
################################################################################
################################################################################
#        order_value = [sym_bol, sym_price, order_condition[item_no], limit_diff_p[item_no],
#                       value_s_list[item_no], value_v_list[item_no]]
def order_calc(order_value):
  itv = 3
  sym_bol = order_value[0]
  sym_price = order_value[1]
  open_order_condition = order_value[2]
  limit_diff = order_value[3]
  s_value_list = order_value[4]
  v_value_list = order_value[5]

#  res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
#  time.sleep(1)
#  position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
#  if(position_idx == 1):
#    long_qty = float(pd.DataFrame(res_ponse)['size'][0])
#    short_qty = float(pd.DataFrame(res_ponse)['size'][1])
#    l_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
#    s_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
#    l_ent_price = pd.DataFrame(res_ponse)['avgPrice'][0]
#    s_ent_price = pd.DataFrame(res_ponse)['avgPrice'][1]
#  else:
#    long_qty = float(pd.DataFrame(res_ponse)['size'][1])
#    short_qty = float(pd.DataFrame(res_ponse)['size'][0])
#    l_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
#    s_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
#    l_ent_price = pd.DataFrame(res_ponse)['avgPrice'][1]
#    s_ent_price = pd.DataFrame(res_ponse)['avgPrice'][0]

#  instruments_info = session.get_instruments_info(category="linear",symbol=sym_bol)['result']['list']
#  time.sleep(1)
#  qty_step = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['qtyStep']
#  min_value = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minNotionalValue']
#  min_qty = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minOrderQty']
#  tick_size = pd.DataFrame(instruments_info)['priceFilter'][0]['tickSize']
#  max_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['maxLeverage']
#  min_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['minLeverage']
#  lever_step = pd.DataFrame(instruments_info)['leverageFilter'][0]['leverageStep']
#-------------------------------------------------------------------------------
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
#  if(open_order_condition == 0) or (open_order_condition != 0):
  turn_num = 0
  ready_p, step_p, end_p = 1, 0, -1
  max_price, min_price = max(h_list), min(l_list)
  max_diff = max_price - min_price
  std_diff = c_list[0] * 0.5 / 5
  min_diff = c_list[0] * 0.5 / 10
  iv_v_list = list(reversed(v_list))
  iv_p_list = list(reversed(p_list))
  tot_v_sum, tot_p_sum = sum(v_list), sum(p_list)
  for v in range(len(v_list)):
    if(sum(iv_v_list[:v]) > (tot_v_sum * 0.5)): break
  for p in range(len(p_list)):
    if(sum(iv_p_list[:p]) > (tot_p_sum * 0.5)): break
  hf_point = min(v, p)
  bk_max_price = max(h_list[(len(h_list) - hf_point):])
  bk_min_price = min(l_list[(len(l_list) - hf_point):])
  fr_max_price = max(h_list[:hf_point])
  fr_min_price = min(l_list[:hf_point])
  bk_diff = bk_max_price - bk_min_price
  mx = h_list[(len(h_list) - hf_point):].index(bk_max_price) + (len(h_list) - hf_point)
  mn = l_list[(len(l_list) - hf_point):].index(bk_min_price) + (len(l_list) - hf_point)
  fr_per = round(bk_diff / (fr_max_price - fr_min_price) * 100, 2)
  xn_per = round(bk_diff / max_diff * 100, 2)
  vl_per = round(sum(iv_v_list[:hf_point]) / tot_v_sum * 100, 2)
#-------------------------------------------------------------------------------
#  if(max_diff < std_diff): limit_diff = max_diff
#  else:
#    open_order_condition = "PASS"
#    s_value_list = [0, max_price, min_price]
#    v_value_list = [0, now_price, round(ready_p,2)]
#    order_return = [open_order_condition, limit_diff, s_value_list, v_value_list]
#    return(order_return)
#-------------------------------------------------------------------------------
  if(bk_max_price > c_list[0]) and (bk_min_price < c_list[0]): order_position = 1
  else: order_position = 0
  if(v_value_list != 0) and (bk_diff != v_value_list[1]): order_position = 0
     
  if(bk_diff < min_diff): limit_diff, step_p = std_diff, 0
  elif(bk_diff > std_diff): limit_diff, step_p = std_diff, 2
  else: limit_diff, step_p = bk_diff, 1

  mx_time = float(t_list[mx] * 0.001)
  mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
  mn_time = float(t_list[mn] * 0.001)
  mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
  hf_time = float(t_list[(len(c_list) - hf_point)] * 0.001)
  hf_server_time = str(datetime.utcfromtimestamp(hf_time) + timedelta(hours=9))
  s_value_list = [step_p, bk_max_price, bk_min_price, fr_per, xn_per, vl_per]
  v_value_list = [order_position, bk_diff, mx_server_time, mn_server_time, hf_server_time]
#-------------------------------------------------------------------------------
  order_return = [open_order_condition, limit_diff, s_value_list, v_value_list]
  return(order_return)
#-------------------------------------------------------------------------------
###############################################################################
def calc_part(order_condition, sym_bol, h_price, l_price, lever_diff):
    instruments_info = session.get_instruments_info(category="linear",symbol=sym_bol)['result']['list']
    time.sleep(1)
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
        if ((liq_l_p < liq_l_limit) and (max_l_perc < lever_point) and (pl <= float(max_lever))):
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

        if ((liq_s_p > liq_s_limit) and (max_s_perc > lever_point) and (ps <= float(max_lever))):
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
item_list = session.get_open_orders(category="linear",settleCoin="USDT")['result']['list']
if(item_list == []): rest_item = []
else: rest_item = pd.DataFrame(item_list)['symbol']
try_item = []
for i in range(len(rest_item)):
  if(rest_item[i] in try_item): pass
  else: try_item.append(rest_item[i])
rest_item = try_item.copy()
#-------------------------------------------------------------------------------
first_time = int(time.time())
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
  values = pd.concat([symbol_list,turnover_list,price_list],axis=1)
  sort_list = values.sort_values('turnover24h',ignore_index=True,ascending=False)
#  added_list = sort_list[(sort_list['lastPrice'] > 0.01) & (sort_list['lastPrice'] < 2) & (sort_list['turnover24h'] > 3e+07)]
  added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e+07)]

  wish_item_no = len(added_list) + len(try_item)
#  if(wish_item_no > 15): wish_item_no = 15
  if(wish_item_no > 10): wish_item_no = 10
  i, j = 0, 0
  while len(try_item) < wish_item_no:
    while i < len(try_item):
      if(j >= len(added_list)): break
      elif(try_item[i] == added_list.iloc[j]['symbol']):
        j = j + 1
        i = 0
      elif(try_item[i] != added_list.iloc[j]['symbol']): i = i + 1

    if(j >= len(added_list)): break
    else: try_item.append(added_list.iloc[j]['symbol'])
    i = 0
#-------------------------------------------------------------------------------
#print(try_item)
#-------------------------------------------------------------------------------
order_usdt, time_t, limit_diff_p = [], [], []
max_margin, min_margin, max_pnl = [], [], []
order_condition, pre_condition, value_s, value_s_list = [], [], [], []
value_v, value_v_list, value_p, value_p_list = [], [], [], []
half_condition, closed_order, wish_price, order_info = [], [], [], []
order_v_add, order_vn_add, order_p_add, keep_item = [], [], [], []

i = 0
while i < len(try_item):
  order_usdt.append(0), time_t.append(0), limit_diff_p.append(0)
  max_margin.append(0), min_margin.append(0), max_pnl.append(0)
  order_condition.append(0), pre_condition.append(0), value_s.append(0), value_s_list.append(0)
  value_v.append(0), value_v_list.append(0), value_p.append(0), value_p_list.append(0)
  half_condition.append(0), closed_order.append(0), wish_price.append(0), order_info.append(0)
  order_v_add.append(0), order_vn_add.append(0), order_p_add.append(0), keep_item.append(0)
  i = i + 1
#-------------------------------------------------------------------------------
i = 0
while i < len(rest_item):
  keep_item[i] = 1
  i = i + 1
#-------------------------------------------------------------------------------
while True:
  btc_info=session.get_tickers(category="linear",symbol='BTCUSDT')['result']['list']
  btc_price = float(pd.DataFrame(btc_info)['lastPrice'][0])
  url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'order_id_Equity = ',round(live_usdt,2), 'My Wallet = ', round(my_usdt,2),'BTCUSDT = ',btc_price}"
#  url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'Test-JQ_BTCUSDT = ',btc_price}"
  requests.get(url).json() # this sends the message  max_usdt = live_usdt
  url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'new_item_list:',try_item}"
  requests.get(url).json() # this sends the message
###############################################################################
  while True:
#-------------------------------------------------------------------------------
    wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
    time.sleep(1)
    my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
    live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
    tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
    avail_usdt = my_usdt - tot_position

    if(max_l_usdt <= live_usdt): max_l_usdt = live_usdt
    if(min_l_usdt >= live_usdt): min_l_usdt = live_usdt
    if(max_m_usdt <= my_usdt): max_m_usdt = my_usdt
    if(min_m_usdt >= my_usdt): min_m_usdt = my_usdt
    if(max_t_position <= tot_position): max_t_position = tot_position

    last_time = int(time.time())
###############################################################################
    for item in try_item:
      item_no = try_item.index(item)
      sym_bol=item
      i_last_time = int(time.time())
      now_time = int(time.time()) * 1000
###############################################################################
      sym_info=session.get_tickers(category="linear",symbol=sym_bol)['result']['list']
#      time.sleep(1)
      sym_price = float(pd.DataFrame(sym_info)['lastPrice'][0])

      res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
      time.sleep(1)
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
      time.sleep(1)
      qty_step = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['qtyStep']
      min_value = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minNotionalValue']
      min_qty = pd.DataFrame(instruments_info)['lotSizeFilter'][0]['minOrderQty']
      tick_size = pd.DataFrame(instruments_info)['priceFilter'][0]['tickSize']
      max_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['maxLeverage']
      min_lever = pd.DataFrame(instruments_info)['leverageFilter'][0]['minLeverage']
      lever_step = pd.DataFrame(instruments_info)['leverageFilter'][0]['leverageStep']

      wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
      time.sleep(1)
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
      time.sleep(1)
      if(m_get_open != []):
        m_order_type = pd.DataFrame(m_get_open)['stopOrderType']
        for num in range(len(m_order_type)): m_order_type_list.append(m_order_type[num])
      m_stop_order_list = [(m_stop_order["positionIdx"],m_stop_order["triggerPrice"], m_stop_order["stopLoss"]) for m_stop_order in m_get_open if m_stop_order.get("stopOrderType") == "Stop"]
      if(m_stop_order_list != []):
        for list in range(len(m_stop_order_list)):
          if(m_stop_order_list[list][0] == 1):
            m_order_idx[1], m_order_tp[1], m_order_st[1] = m_stop_order_list[list][0], float(m_stop_order_list[list][1]), float(m_stop_order_list[list][2])
          if(m_stop_order_list[list][0] == 2):
            m_order_idx[2], m_order_tp[2], m_order_st[2] = m_stop_order_list[list][0], float(m_stop_order_list[list][1]), float(m_stop_order_list[list][2])
#-------------------------------------------------------------------------------
      l_order_type_list = []
      l_order_idx, l_order_tp, l_order_st = [0, 0, 0], [0, 0, 0], [0, 0, 0]
      l_get_open=session.get_open_orders(category="linear",symbol=sym_bol,orderFilter='Order')['result']['list']
      time.sleep(1)
      if(l_get_open != []):
        l_order_type = pd.DataFrame(l_get_open)['orderType']
        for num in range(len(l_order_type)): l_order_type_list.append(l_order_type[num])
      l_stop_order_list = [(l_stop_order["positionIdx"],l_stop_order["price"], l_stop_order["stopLoss"]) for l_stop_order in l_get_open if l_stop_order.get("orderType") == "Limit"]
      if(l_stop_order_list != []):
        for list in range(len(l_stop_order_list)):
          if(l_stop_order_list[list][0] == 1):
            l_order_idx[1], l_order_tp[1], l_order_st[1] = l_stop_order_list[list][0], float(l_stop_order_list[list][1]), float(l_stop_order_list[list][2])
          if(l_stop_order_list[list][0] == 2):
            l_order_idx[2], l_order_tp[2], l_order_st[2] = l_stop_order_list[list][0], float(l_stop_order_list[list][1]), float(l_stop_order_list[list][2])
#-------------------------------------------------------------------------------
#      if(m_get_open != []): keep_item[item_no] = 1
      if(long_qty != 0) or (short_qty != 0): keep_item[item_no] = 1
      else: keep_item[item_no] = 0
#      if(order_condition[item_no] == 0) and ((long_qty != 0) or (short_qty != 0)): keep_item[item_no] = 1
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
      now_order_state = 0
      if(long_qty != 0):  now_order_state = 1
      if(short_qty != 0): now_order_state = 2
      if(long_qty != 0) and (short_qty != 0): now_order_state = 3
      if(long_qty == 0) and (now_order_state != closed_order[item_no]) and ((closed_order[item_no] == 1) or (closed_order[item_no] == 3)):
        pnl_list = session.get_closed_pnl(category="linear",symbol=sym_bol,limit=1)['result']['list']
#        time.sleep(1)
        if(pnl_list == []): pnl = [0]
        else: pnl = (pd.DataFrame(pnl_list)['closedPnl'])
        closed_order_info = [sym_bol, 'Long_closed', round(float(pnl[0]),2), round(my_usdt,2), round(live_usdt,2), order_info[item_no]]
        url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={closed_order_info}"
        requests.get(url).json() # this sends the message
        closed_order[item_no] = 0
        order_condition[item_no] = 0
      if(short_qty == 0) and (now_order_state != closed_order[item_no]) and ((closed_order[item_no] == 2) or (closed_order[item_no] == 3)):
        pnl_list = session.get_closed_pnl(category="linear",symbol=sym_bol,limit=1)['result']['list']
#        time.sleep(1)
        if(pnl_list == []): pnl = [0]
        else: pnl = (pd.DataFrame(pnl_list)['closedPnl'])
        closed_order_info = [sym_bol, 'Short_closed', round(float(pnl[0]),2), round(my_usdt,2), round(live_usdt,2), order_info[item_no]]
        url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={closed_order_info}"
        requests.get(url).json() # this sends the message

      if(long_qty != 0) and (now_order_state != closed_order[item_no]) and (closed_order[item_no] == 0):
        opened_order_info = [sym_bol, round(float(l_position_im),1), pre_condition[item_no], order_condition[item_no], order_info[item_no]]
        url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
        requests.get(url).json() # this sends the message

      if(short_qty != 0) and (now_order_state != closed_order[item_no]) and (closed_order[item_no] == 0):
        opened_order_info = [sym_bol, round(float(s_position_im),1), pre_condition[item_no], order_condition[item_no], order_info[item_no]]
        url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
        requests.get(url).json() # this sends the message

      closed_order[item_no] = now_order_state
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
      if(sum(keep_item) >= ordered_item) and (keep_item[item_no] == 0):
        if(m_get_open != []):
          session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
        if(l_get_open != []):
          session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='Order')
        order_condition[item_no] = 0
        order_info[item_no] = 0
        pass
      else:
#-------------------------------------------------------------------------------
#START
#-------------------------------------------------------------------------------
        if(order_condition[item_no] != 0): pre_condition[item_no] = order_condition[item_no]
        if(order_condition[item_no] == 0):
          if(long_qty != 0):  order_condition[item_no] = 'pre_L_open'
          if(short_qty != 0): order_condition[item_no] = 'pre_S_open'
          if(long_qty != 0) and (short_qty != 0): order_condition[item_no] = 'pre_Both_open'
          if(long_qty == 0) and (short_qty == 0) and ((l_get_open != []) or (m_get_open != [])):
            order_condition[item_no] = 'pre_order'
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
        h_price, l_price = value_s_list[item_no][1], value_s_list[item_no][2]
#        hh_price, ll_price = value_s_list[item_no][1] + limit_diff_p[item_no], value_s_list[item_no][2] - limit_diff_p[item_no]
#-------------------------------------------------------------------------------
# calc_part_result
# calc_return = [sym_bol, l_new_lever, s_new_lever]
        calc_result = calc_part(order_condition[item_no], sym_bol, h_price, l_price, limit_diff_p[item_no])
#-------------------------------------------------------------------------------
        if(long_qty == 0) and (float(calc_result[1]) != float(l_sym_lever)):
          session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=calc_result[1], sellLeverage=s_sym_lever)
          time.sleep(1)
        if(short_qty == 0) and (float(calc_result[2]) != float(s_sym_lever)):
          session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=l_sym_lever, sellLeverage=calc_result[2])
          time.sleep(1)

        res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
        time.sleep(1)
        position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
        if(position_idx == 1):
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
        else:
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]

#        if((float(calc_result[1]) * 1.1) < float(l_sym_lever)): l_sym_lever = calc_result[1]
#        if((float(calc_result[2]) * 1.1) < float(s_sym_lever)): s_sym_lever = calc_result[2]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        l_ex_price = str(h_price + float(tick_size))
        l_order_price = str(int(Decimal(l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_ex_qty = str((invest_usdt * float(l_sym_lever)) / float(l_order_price))
        l_order_qty = str(int(Decimal(l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        l_st_ex_price = str(h_price - limit_diff_p[item_no] - float(tick_size))
        l_st_price = str(int(Decimal(l_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_order_side = 'Buy'
        l_order_position = 1
        l_ex_value = float(l_order_qty) * float(l_order_price) * 0.8

        s_ex_price = str(l_price - float(tick_size))
        s_order_price = str(int(Decimal(s_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_ex_qty = str((invest_usdt * float(s_sym_lever)) / float(s_order_price))
        s_order_qty = str(int(Decimal(s_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        s_st_ex_price = str(l_price + limit_diff_p[item_no] + float(tick_size))
        s_st_price = str(int(Decimal(s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_order_side = 'Sell'
        s_order_position = 2
        s_ex_value = float(s_order_qty) * float(s_order_price) * 0.8

        if(value_v_list[item_no][0] in (3, 5)):
            m_l_ex_price = str(h_price + float(tick_size))
            m_l_order_price = str(int(Decimal(m_l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            m_l_ex_qty = str((invest_usdt * float(l_sym_lever)) / float(m_l_order_price))
            m_l_order_qty = str(int(Decimal(m_l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
            m_l_st_ex_price = str(l_price - float(tick_size))
            m_l_st_price = str(int(Decimal(m_l_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            m_l_order_side = 'Buy'
            m_l_order_position = 1
            m_l_ex_value = float(m_l_order_qty) * float(m_l_order_price) * 0.8

            l_l_ex_price = str(l_price - float(tick_size))
            l_l_order_price = str(int(Decimal(l_l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            l_l_ex_qty = str((invest_usdt * float(l_sym_lever)) / float(l_l_order_price))
            l_l_order_qty = str(int(Decimal(l_l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
            l_l_st_ex_price = str(ll_price - float(tick_size))
            l_l_st_price = str(int(Decimal(l_l_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            l_l_order_side = 'Buy'
            l_l_order_position = 1
            l_l_ex_value = float(l_l_order_qty) * float(l_l_order_price) * 0.8

            m_s_order_price, m_s_order_qty, m_s_st_price, m_s_ex_value = 0, 0, 0, 0
            l_s_order_price, l_s_order_qty, l_s_st_price, l_s_ex_value = 0, 0, 0, 0

        elif(value_v_list[item_no][0] in (4, 6)):
            l_s_ex_price = str(h_price + float(tick_size))
            l_s_order_price = str(int(Decimal(l_s_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            l_s_ex_qty = str((invest_usdt * float(s_sym_lever)) / float(l_s_order_price))
            l_s_order_qty = str(int(Decimal(l_s_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
            l_s_st_ex_price = str(hh_price + float(tick_size))
            l_s_st_price = str(int(Decimal(l_s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            l_s_order_side = 'Sell'
            l_s_order_position = 2
            l_s_ex_value = float(l_s_order_qty) * float(l_s_order_price) * 0.8

            m_s_ex_price = str(l_price - float(tick_size))
            m_s_order_price = str(int(Decimal(m_s_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            m_s_ex_qty = str((invest_usdt * float(s_sym_lever)) / float(m_s_order_price))
            m_s_order_qty = str(int(Decimal(m_s_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
            m_s_st_ex_price = str(h_price + float(tick_size))
            m_s_st_price = str(int(Decimal(m_s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            m_s_order_side = 'Sell'
            m_s_order_position = 2
            m_s_ex_value = float(m_s_order_qty) * float(m_s_order_price) * 0.8

            m_l_order_price, m_l_order_qty, m_l_st_price, m_l_ex_value = 0, 0, 0, 0
            l_l_order_price, l_l_order_qty, l_l_st_price, l_l_ex_value = 0, 0, 0, 0
                      
        else:
            m_l_order_price, m_l_order_qty, m_l_st_price, m_s_order_price, m_s_order_qty, m_s_st_price, m_l_ex_value, m_s_ex_value = 0, 0, 0, 0, 0, 0, 0, 0
            l_l_order_price, l_l_order_qty, l_l_st_price, l_s_order_price, l_s_order_qty, l_s_st_price, l_l_ex_value, l_s_ex_value = 0, 0, 0, 0, 0, 0, 0, 0
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(order_condition[item_no] == 'pre_order'):
          if(m_order_st[1] < m_order_tp[1]): order_condition[item_no] = 'pre_L_order'
          if(l_order_st[1] < l_order_tp[1]): order_condition[item_no] = 'pre_L_order'
          if(m_order_st[2] > m_order_tp[2]): order_condition[item_no] = 'pre_S_order'
          if(l_order_st[2] > l_order_tp[2]): order_condition[item_no] = 'pre_S_order'
          order_info[item_no] = [value_s_list[item_no], value_v_list[item_no]]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(value_v_list[item_no][0] == 0):
#          if(l_order_idx[1] == 1):
#            session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='Order')
#            order_condition[item_no] = 'L_order_cancel'
#            time.sleep(1)
          if(m_order_idx[1] == 1) or (m_order_idx[2] == 2):
            session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
            order_condition[item_no] = 'order_cancel'
            time.sleep(1)

#        if(value_v_list[item_no][0] not in (2, 4)):
#          if(l_order_idx[2] == 2):
#            session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='Order')
#            order_condition[item_no] = 'L_order_cancel'
#            time.sleep(1)
#          if(m_order_idx[2] == 2):
#            session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#            order_condition[item_no] = 'S_order_cancel'
#            time.sleep(1)
          
#        if(value_v_list[item_no][0] == 1) and (l_order_idx[1] == 1):
#            if(l_order_st[1] > float(l_l_st_price)):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='Order')
#              time.sleep(1)
#              order_condition[item_no] = 'L_limit_order_cancel'

#        if(value_v_list[item_no][0] == 4) and (l_order_idx[2] == 2):
#            if(l_order_st[2] < float(l_s_st_price)):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='Order')
#              time.sleep(1)
#              order_condition[item_no] = 'S_limit_order_cancel'
#-------------------------------------------------------------------------------
###############################################################################
#        if(long_qty != 0) and (float(l_unpnl) >= (invest_usdt * 0.1)) and (value_v_list[item_no][0] == 2):  
#            add_order = [sym_bol, "Sell", 1]
#            closed_order_part(add_order)
#            time.sleep(1)
#            order_condition[item_no] = 'PF_L_closed'
#            order_info[item_no] = [value_s_list[item_no], value_v_list[item_no]]
##            opened_order_info = [sym_bol, l_unpnl, order_condition[item_no], order_info[item_no]]
##            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
##            requests.get(url).json() # this sends the message
            
#        if(short_qty != 0) and (float(s_unpnl) >= (invest_usdt * 0.1)) and (value_v_list[item_no][0] == 1):  
#            add_order = [sym_bol, "Buy", 2]
#            closed_order_part(add_order)
#            time.sleep(1)
#            order_condition[item_no] = 'PF_S_closed'
#            order_info[item_no] = [value_s_list[item_no], value_v_list[item_no]]
##            opened_order_info = [sym_bol, s_unpnl, order_condition[item_no], order_info[item_no]]
##            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
##            requests.get(url).json() # this sends the message
###############################################################################
#-------------------------------------------------------------------------------
        res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
        time.sleep(1)
        position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
        if(position_idx == 1):
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
        else:
          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(value_s_list[item_no][0] == 1) and (value_s_list[item_no][1] > sym_price > value_s_list[item_no][2]):
#        if(value_s_list[item_no][0] != 0) and (value_v_list[item_no][0] != 0):
#-------------------------------------------------------------------------------
#          if(m_get_open == []) and (l_get_open == []):
#-------------------------------------------------------------------------------
            if(long_qty == 0) and ((invest_usdt * 2) < avail_usdt) and (float(l_sym_lever) == float(calc_result[1])):
                if(value_v_list[item_no][0] == 1) and (m_order_idx[1] == 0):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
#                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_st_price]                  
#                    order_market_part(add_order)
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, l_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
#                    order_condition[item_no] = 'L_market_order'
                    order_info[item_no] = [value_s_list[item_no], value_v_list[item_no]]
#                    opened_order_info = [sym_bol, order_condition[item_no], order_info[item_no]]
#                    url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
#                    requests.get(url).json() # this sends the message
                      
#                  if(float(min_value) < l_l_ex_value) and (l_order_idx[1] == 0) and (float(l_l_order_qty) != 0):
#                    add_order = [sym_bol, 'Buy', l_l_order_qty, l_l_order_price, 1, l_l_st_price]
#                    order_limit_part(add_order)
#                    time.sleep(1)
#                  if(float(min_value) < m_l_ex_value) and (m_order_idx[1] == 0) and (float(m_l_order_qty) != 0):
#                    add_order = [sym_bol, 'Buy', m_l_order_qty, 1, m_l_order_price, 1, m_l_st_price]
#                    conditional_market_part(add_order)
#                    time.sleep(1)
                      
#                if(value_v_list[item_no][0] == 3):
#                  if(float(min_value) < l_l_ex_value) and (l_order_idx[1] == 0) and (float(l_l_order_qty) != 0):
#                    add_order = [sym_bol, 'Buy', l_l_order_qty, l_l_order_price, 1, l_l_st_price]
#                    order_limit_part(add_order)
#                    time.sleep(1)
#                  if(float(min_value) < m_l_ex_value) and (m_order_idx[1] == 0) and (float(m_l_order_qty) != 0):
#                    add_order = [sym_bol, 'Buy', m_l_order_qty, 1, m_l_order_price, 1, m_l_st_price]
#                    conditional_market_part(add_order)
#                    time.sleep(1)
#                    order_condition[item_no] = 'L3_limit_order'
#                    order_info[item_no] = [value_s_list[item_no], value_v_list[item_no]]

            if(short_qty == 0) and ((invest_usdt * 2) < avail_usdt) and (float(s_sym_lever) == float(calc_result[2])):
                if(value_v_list[item_no][0] == 2) and (m_order_idx[2] == 0):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, s_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
#                    order_condition[item_no] = 'S_market_order'
                    order_info[item_no] = [value_s_list[item_no], value_v_list[item_no]]
#                    opened_order_info = [sym_bol, order_condition[item_no], order_info[item_no]]
#                    url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
#                    requests.get(url).json() # this sends the message
                    
#                  if(float(min_value) < l_s_ex_value) and (l_order_idx[2] == 0) and (float(l_s_order_qty) != 0):
#                    add_order = [sym_bol, 'Sell', l_s_order_qty, l_s_order_price, 2, l_s_st_price]
#                    order_limit_part(add_order)
#                    time.sleep(1)
#                  if(float(min_value) < m_s_ex_value) and (m_order_idx[2] == 0) and (float(m_s_order_qty) != 0):
#                    add_order = [sym_bol, 'Sell', m_s_order_qty, 2, m_s_order_price, 2, m_s_st_price]
#                    conditional_market_part(add_order)
#                    time.sleep(1)

#                if(value_v_list[item_no][0] == 4):
#                  if(float(min_value) < l_s_ex_value) and (l_order_idx[2] == 0) and (float(l_s_order_qty) != 0):
#                    add_order = [sym_bol, 'Sell', l_s_order_qty, l_s_order_price, 2, l_s_st_price]
#                    order_limit_part(add_order)
#                    time.sleep(1)
#                  if(float(min_value) < m_s_ex_value) and (m_order_idx[2] == 0) and (float(m_s_order_qty) != 0):
#                    add_order = [sym_bol, 'Sell', m_s_order_qty, 2, m_s_order_price, 2, m_s_st_price]
#                    conditional_market_part(add_order)
#                    time.sleep(1)
#                    order_condition[item_no] = 'S4_limit_order'
#                    order_info[item_no] = [value_s_list[item_no], value_v_list[item_no]]
#-------------------------------------------------------------------------------
        if(long_qty != 0):
          ex_act_price = str(float(l_ent_price) + (abs(float(l_ent_price) - float(l_st_loss))))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(l_trailing) == 0):
            ex_ts_diff = abs(float(l_ent_price) - float(l_st_loss))
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 1]
            set_trading_stop_item(add_order)
#            order_condition[item_no] = 'L_open'

            time.sleep(1)
#            opened_order_info = [sym_bol, round(float(l_position_im),1), pre_condition[item_no], order_condition[item_no], order_info[item_no]]
#            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
#            requests.get(url).json() # this sends the message
#
#            if(l_order_idx[1] == 1):
#              session.cancel_all_orders(category="linear", symbol=sym_bol, orderFilter='Order')
#              time.sleep(1)
#            if(m_order_idx[1] == 1):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#              time.sleep(1)
#-------------------------------------------------------------------------------
        if(short_qty != 0):
          ex_act_price = str(float(s_ent_price) - (abs(float(s_ent_price) - float(s_st_loss))))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(s_trailing) == 0):
            ex_ts_diff = abs(float(s_ent_price) - float(s_st_loss))
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 2]
            set_trading_stop_item(add_order)
#            order_condition[item_no] = 'S_open'

            time.sleep(1)
#            opened_order_info = [sym_bol, round(float(s_position_im),1), pre_condition[item_no], order_condition[item_no], order_info[item_no]]
#            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
#            requests.get(url).json() # this sends the message
#
#            if(l_order_idx[2] == 2):
#              session.cancel_all_orders(category="linear", symbol=sym_bol, orderFilter='Order')
#              time.sleep(1)
#            if(m_order_idx[2] == 2):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#              time.sleep(1)
#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
##        if(long_qty != 0) and (value_s_list[item_no][0] in (2, 4)) and (value_v_list[item_no][2] > sym_price):
#        if(long_qty != 0) and (value_v_list[item_no][2] > sym_price):
#          add_order = [sym_bol, "Sell", 1]
#          closed_order_part(add_order)
#          time.sleep(1)
#          if(float(l_unpnl) > 0): order_condition[item_no] = 'PF_L_closed'
#          else: order_condition[item_no] = 'SL_L_closed'
#          opened_order_info = [sym_bol, pre_condition[item_no], order_condition[item_no], round(float(l_position_im),1)]
#          url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
#          requests.get(url).json() # this sends the message
#
##        if(short_qty != 0) and (value_s_list[item_no][0] in (1, 3)) and (value_v_list[item_no][1] < sym_price):
#        if(short_qty != 0) and (value_v_list[item_no][1] < sym_price):
#          add_order = [sym_bol, "Buy", 2]
#          closed_order_part(add_order)
#          time.sleep(1)
#          if(float(s_unpnl) > 0): order_condition[item_no] = 'PF_S_closed'
#          else: order_condition[item_no] = 'SL_S_closed'
#          opened_order_info = [sym_bol, pre_condition[item_no], order_condition[item_no], round(float(s_position_im),1)]
#          url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
#          requests.get(url).json() # this sends the message
#
###############################################################################
        if (long_qty != 0):
          print(sym_bol,sym_price,'order_condition:',pre_condition[item_no], order_condition[item_no],'now_m:',l_unpnl)
        elif (short_qty != 0):
          print(sym_bol,sym_price,'order_condition:',pre_condition[item_no], order_condition[item_no],'now_m:',s_unpnl)
        else:
          print(sym_bol,sym_price,pre_condition[item_no],order_condition[item_no], 'PASS')
        print('lever_ex_value:',calc_result[1], calc_result[2])
        print('value_s:',value_s_list[item_no])
        print('value_v:',value_v_list[item_no])

###############################################################################
#        time.sleep(2)
        i_this_time = int(time.time())
        i_diff_time = i_this_time - i_last_time
        i_rest_time = int(6 - i_diff_time)
        if(i_rest_time > 0): time.sleep(i_rest_time)
###############################################################################
    this_time = int(time.time())
    diff_time = this_time - last_time
    rest_time = int(60 - diff_time)
    if(rest_time > 0): time.sleep(rest_time)
    check_time = check_time + 1
    if(check_time > 300):
      run_time = int(time.time())
      one_cycle = round((run_time - first_time) / (60 * 60),1)
      first_time = int(time.time())
      url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'one_cycle(hr):',one_cycle}"
      requests.get(url).json() # this sends the message
      check_time = 0
###############################################################################
##      tickers = session.get_tickers(category="linear")['result']['list']
##      symbol_list = (pd.DataFrame(tickers)['symbol'])
##      turnover_list = (pd.DataFrame(tickers)['turnover24h']).astype(float)
##      price_list = (pd.DataFrame(tickers)['lastPrice']).astype(float)
##      values = pd.concat([symbol_list,turnover_list,price_list],axis=1)
##      sort_list = values.sort_values('turnover24h',ignore_index=True,ascending=False)
###      added_list = sort_list[(sort_list['lastPrice'] > 0.01) & (sort_list['lastPrice'] < 2) & (sort_list['turnover24h'] > 3e+07)]
##      added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e+07)]
##      del_list = sort_list[(sort_list['turnover24h'] < 2e+07)]
#-------------------------------------------------------------------------------
# deleted item
##      i, j = 0, 0
##      now_item_no = len(try_item)
##      while i < len(try_item):
##        while j < len(del_list):
##          if(len(try_item) <= i) or (len(del_list) <= j): break
##          if(try_item[i] == del_list.iloc[j]['symbol']):
#-------------------------------------------------------------------------------
##            res_ponse=session.get_positions(category="linear",symbol=try_item[i])['result']['list']
##            long_qty = float(pd.DataFrame(res_ponse)['size'][0])
##            short_qty = float(pd.DataFrame(res_ponse)['size'][1])
##            if(long_qty != 0):
##                del_long_closed_item(try_item[i])
##                time.sleep(1)
##                url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'del_long_closed_item:',try_item[i]}"
##                requests.get(url).json() # this sends the message
##            if(short_qty != 0):
##                del_short_closed_item(try_item[i])
##                time.sleep(1)
##                url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'del_short_closed_item:',try_item[i]}"
##                requests.get(url).json() # this sends the message
#-------------------------------------------------------------------------------
##            try_item.remove(try_item[i])
##            order_usdt.remove(order_usdt[i]), time_t.remove(time_t[i]), limit_diff_p.remove(limit_diff_p[i])
##            max_margin.remove(max_margin[i]), min_margin.remove(min_margin[i]), max_pnl.remove(max_pnl[i])
##            order_condition.remove(order_condition[i]), pre_condition.remove(pre_condition[i]), value_s.remove(value_s[i]), value_s_list.remove(value_s_list[i])
##            value_v.remove(value_v[i]), value_v_list.remove(value_v_list[i]), value_p.remove(value_p[i]), value_p_list.remove(value_p_list[i])
##            half_condition.remove(half_condition[i]), closed_order.remove(closed_order[i]), wish_price.remove(wish_price[i]), order_info.remove(order_info[i])
##            order_v_add.remove(order_v_add[i]), order_vn_add.remove(order_vn_add[i]), order_p_add.remove(order_p_add[i]), keep_item.remove(keep_item[i])
##            j = 0
##          else:
##            j = j + 1
##        i = i + 1
##        j = 0
##        if(len(try_item) <= i): break
#-------------------------------------------------------------------------------
#    print(try_item)
#-------------------------------------------------------------------------------
# added item
##      if(now_item_no > len(try_item)):
##        wish_item_no = len(added_list) + len(try_item)
##        if(wish_item_no > 15): wish_item_no = 15
##        i, j = 0, 0
##        while len(try_item) < wish_item_no:
##          while i < len(try_item):
##            if(j >= len(added_list)): break
##            elif(try_item[i] == added_list.iloc[j]['symbol']):
##              j = j + 1
##              i = 0
##            elif(try_item[i] != added_list.iloc[j]['symbol']): i = i + 1
##          if(j >= len(added_list)): break
##          else:
##            try_item.append(added_list.iloc[j]['symbol'])
##            order_usdt.append(0), time_t.append(0), limit_diff_p.append(0)
##            max_margin.append(0), min_margin.append(0), max_pnl.append(0)
##            order_condition.append(0), pre_condition.append(0), value_s.append(0), value_s_list.append(0)
##            value_v.append(0), value_v_list.append(0), value_p.append(0), value_p_list.append(0)
##            half_condition.append(0), closed_order.append(0), wish_price.append(0), order_info.append(0)
##            order_v_add.append(0), order_vn_add.append(0), order_p_add.append(0), keep_item.append(0)
##          i = 0
##        url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'new_item_list:',try_item}"
##        requests.get(url).json() # this sends the message
##      else:
##        url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'Not change_item'}"
##        requests.get(url).json() # this sends the message
#-------------------------------------------------------------------------------
#    print(try_item)
#-------------------------------------------------------------------------------
###############################################################################
    korea_tz = pytz.timezone('Asia/Seoul')
    current_time_korea = datetime.now(korea_tz)
    current_time = current_time_korea.strftime('%Y-%m-%d %H:%M:%S')
    print('l_USDT_MAX_MIN :',round(max_l_usdt,2),round(min_l_usdt,2),'live_USDT: ',round(live_usdt,2))
    print('m_USDT_MAX_MIN :',round(max_m_usdt,2),round(min_m_usdt,2),'my_USDT: ',round(my_usdt,2),'origin_usdt:',round(origin_usdt,2))
    print('T_POSITION_MAX_NOW :',round(max_t_position,2),round(tot_position,2),'invest_USDT:',round(invest_usdt,1))
    print(current_time,'check_time =',check_time,'keep_item',sum(keep_item),'Reset')
#    print(calc_result[0],'try_num:',try_num,'Reset')
#    print(calc_result[0],'try_num:',try_num,'Reset')
