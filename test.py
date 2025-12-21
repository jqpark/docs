#v5_test14-12-10_SMA020_251211-1200
#v5 api
#Optimization <- v5_test13-6-3_SMA020_250619-1700
#problume -> v5_test14-9-4_JQPARK_251014-1730 -> v5_test13-6-2_JQPARK_250523-1620 - retry code
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

order_id = SMA000

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
def search_calc(search_list):
  order_list = []
  min_lever = 10 
  remainder = 5  
  for item in range(len(search_list)):  
    itv = 3
    sym_bol = search_list[item]
    get_kline=session.get_kline(category="linear",symbol=sym_bol,interval=str(itv),limit=1000)['result']['list']
    if(item / remainder == 0): time.sleep(1)
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
    for lx in range(1,len(c_list)):
      if((max(h_list[:lx]) - min(l_list[:lx])) >= (c_list[0] * 0.5 / 5) * 2): break
    nmx_diff = max(h_list[:lx-1]) - min(l_list[:lx-1])
    std = lx-1
    std_diff = nmx_diff
    max_diff = max(h_list) - min(l_list)
    mx_price, mn_price = max(h_list[:std]), min(l_list[:std])
    mx_point, mn_point = h_list.index(mx_price), l_list.index(mn_price)
    if(mx_point < mn_point) and (mx_point != 0):
      new_max = mx_price
      new_min = min(l_list[:mx_point])
      max_num = mx_point
      min_num = l_list.index(new_min)
      bk_vol = sum(v_list[max_num:mn_point])
      fr_vol = sum(v_list[:max_num])
      cal_diff = max(h_list[:mn_point]) - min(l_list[:mn_point])
      vol_per = round(fr_vol / bk_vol * 100,2)
    elif(mx_point > mn_point) and (mn_point != 0):
      new_max = max(h_list[:mn_point])
      new_min = mn_price
      max_num = h_list.index(new_max)
      min_num = mn_point
      bk_vol = sum(v_list[min_num:mx_point])
      fr_vol = sum(v_list[:min_num])
      cal_diff = max(h_list[:mx_point]) - min(l_list[:mx_point]) 
      vol_per = round(fr_vol / bk_vol * 100,2)
    else:
      new_max = mx_price
      new_min = mn_price
      max_num = mx_point
      min_num = mn_point
      bk_vol = sum(v_list[max_num:min_num])
      fr_vol = sum(v_list[:max_num])
      cal_diff = h_list[max_num] - l_list[min_num]
      vol_per = 0

    new_diff = new_max - new_min
    new_per = round(new_diff / std_diff * 100,2)
    new_lever = round(c_list[0] * 0.5 / new_diff,2) 
    cal_lever = round(c_list[0] * 0.5 / cal_diff,2)
    all_lever = round(c_list[0] * 0.5 / max_diff,2)
    if(bk_vol != 0) and (fr_vol != 0):
      vl_per = round((new_diff / fr_vol) / (cal_diff / bk_vol) * 100,2)
    else: vl_per = 0
    print(sym_bol,mx_point,mn_point,max_num,min_num)
    print(sym_bol,vl_per,vol_per,new_lever,cal_lever,all_lever)
    if(new_lever > (cal_lever * 2)) and (new_lever < min_lever): order_list.append(sym_bol)
  return(order_list)  
################################################################################
def order_calc(sym_bol):
  itv = 3
  order_condition = 0
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
  for lx in range(1,len(c_list)):
      if((max(h_list[:lx]) - min(l_list[:lx])) >= (c_list[0] * 0.5 / 5) * 2): break
  nmx_diff = max(h_list[:lx-1]) - min(l_list[:lx-1])
  std = lx-1
  std_diff = nmx_diff
  max_diff = max(h_list) - min(l_list)
  mx_price, mn_price = max(h_list[:std]), min(l_list[:std])
  mx_point, mn_point = h_list.index(mx_price), l_list.index(mn_price)
  if(mx_point < mn_point) and (mx_point != 0):
      new_max = mx_price
      new_min = min(l_list[:mx_point])
      max_num = mx_point
      min_num = l_list.index(new_min)
      bk_vol = sum(v_list[max_num:mn_point])
      fr_vol = sum(v_list[:max_num])
      cal_diff = max(h_list[:mn_point]) - min(l_list[:mn_point])
      vol_per = round(fr_vol / bk_vol * 100,2)
  elif(mx_point > mn_point) and (mn_point != 0):
      new_max = max(h_list[:mn_point])
      new_min = mn_price
      max_num = h_list.index(new_max)
      min_num = mn_point
      bk_vol = sum(v_list[min_num:mx_point])
      fr_vol = sum(v_list[:min_num])
      cal_diff = max(h_list[:mx_point]) - min(l_list[:mx_point]) 
      vol_per = round(fr_vol / bk_vol * 100,2)
  else:
      new_max = mx_price
      new_min = mn_price
      max_num = mx_point
      min_num = mn_point
      bk_vol = sum(v_list[max_num:min_num])
      fr_vol = sum(v_list[:max_num])
      cal_diff = h_list[max_num] - l_list[min_num]
      vol_per = 0

  new_diff = new_max - new_min
  new_per = round(new_diff / std_diff * 100,2)
  min_diff = c_list[0] * 0.5 / 10
  min_lever = round(c_list[0] * 0.5 / min_diff,2)
  new_lever = round(c_list[0] * 0.5 / new_diff,2) 
  cal_lever = round(c_list[0] * 0.5 / cal_diff,2)
  all_lever = round(c_list[0] * 0.5 / max_diff,2)
  if(bk_vol != 0) and (fr_vol != 0):
      vl_per = round((new_diff / fr_vol) / (cal_diff / bk_vol) * 100,2)
  else: vl_per = 0
  print(sym_bol,mx_point,mn_point,max_num,min_num)
  print(sym_bol,vl_per,vol_per,new_lever,cal_lever,all_lever)
  if(new_lever > (cal_lever * 2)) and (new_lever < min_lever): order_position = 1
  limit_diff_1 = c_list[0] * 0.5 / 5
  limit_diff_2 = new_diff * 1.2
  limit_diff = min(limit_diff_1, limit_diff_2)
#  mx_time = float(t_list[mx] * 0.001)
#  mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
#  mn_time = float(t_list[mn] * 0.001)
#  mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
#  s_value_list = [step_p, round(liner_per,2), round(v_p_per,2), round(p_p_per,2), round(l_p_per,2)]
#  v_value_list = [order_position, maxd_per, mx_server_time, mn_server_time]
#-------------------------------------------------------------------------------
  order_return = [order_position, new_max, new_min, limit_diff]
  return(order_return)
#-------------------------------------------------------------------------------
###############################################################################
def calc_part(sym_bol, h_price, l_price, lever_diff):
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

  item_list = pd.DataFrame(session.get_open_orders(category="linear",settleCoin="USDT",orderFilter='StopOrder',limit=50)['result']['list'])
  if item_list.empty: except_list, open_list, Trail_list = [], [], []
  else:
    open_list = list(set(item_list['symbol'].to_list()))
    Trail_list = item_list[(item_list['stopOrderType'] == 'TrailingStop')]
    check_condition = lambda x: {1, 2}.issubset(set(x))
    double_list = item_list[item_list.groupby('symbol')['positionIdx'].transform(check_condition)]
    except_list = list(set(pd.concat([Trail_list,double_list],axis=0)["symbol"].tolist()))
  set_except = set(except_list)
  rest_list = [item for item in open_list if item not in set_except]

  get_positions = session.get_positions(category="linear",settleCoin="USDT")['result']['list']
  if(get_positions == []): get_item, get_list = [], []
  else: 
    get_item = pd.DataFrame(get_positions)['symbol']
    get_list = get_item.tolist()

  del_list = session.get_announcement(locale="en-US",type='Delistings',tag='Derivatives')['result']['list']
  if(del_list == []): title_list = []
  else: title_list = [item['title'] for item in del_list]
  all_words = []
  for title in title_list:
    all_words.extend(re.findall(r'\b\w+\b', title)) 
  uppercase_words = {word for word in all_words if word.isupper()}
  final_del_list = sorted(list(uppercase_words))
#rest_item = try_item.copy()
#-------------------------------------------------------------------------------
#  first_time = int(time.time())
#-------------------------------------------------------------------------------
# add item list
  ordered_item = 10
  #wish_item_no = 15
  wish_item_no = 10
  tickers = session.get_tickers(category="linear")['result']['list']
  symbol_list = (pd.DataFrame(tickers)['symbol'])
  turnover_list = (pd.DataFrame(tickers)['turnover24h']).astype(float)
  price_list = (pd.DataFrame(tickers)['lastPrice']).astype(float)
  diff_list = (pd.DataFrame(tickers)['price24hPcnt']).astype(float)  
  values = pd.concat([symbol_list,turnover_list,price_list,diff_list],axis=1)
  sort_list = values.sort_values('price24hPcnt',key=lambda x: x.abs(),ignore_index=True,ascending=False)
#  added_list = sort_list[(sort_list['lastPrice'] > 0.01) & (sort_list['lastPrice'] < 2) & (sort_list['turnover24h'] > 3e+07)]
  added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e+07)]
  added_symbols = added_list["symbol"].tolist()
  added_symbols = [x for x in added_symbols if x not in open_list]
  added_symbols = [x for x in added_symbols if x not in final_del_list]
  added_symbols = [x for x in added_symbols if 'USDT' in x]

#  for i in range(len(rest_list)):
#      if(len(try_item) >= wish_item_no): break
#      try_item.append(rest_list[i])

#  for i in range(len(added_symbols)):
#      if(len(try_item) >= wish_item_no): break
#      try_item.append(added_symbols[i])
#-------------------------------------------------------------------------------
  search_item = added_symbols  
# order_calc
  if(search_item == []): search_result = []
  else: search_result = search_calc(search_item)
  if(search_result == []): order_result = []
  else:
      for sym_bol in search_result:
        order_result = order_calc(sym_bol)
#          if(order_result[0] != 0):
#-------------------------------------------------------------------------------
# calc_part_result
        h_price, l_price, limit_diff = order_result[1], order_result[2], order_result[3]
        calc_result = calc_part(sym_bol, h_price, l_price, limit_diff)              
# calc_return = [sym_bol, l_new_lever, s_new_lever]
#-------------------------------------------------------------------------------
        sym_info=session.get_tickers(category="linear",symbol=sym_bol)['result']['list']
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
        status = instruments_info[0]['status']
#-------------------------------------------------------------------------------
        if(float(max_lever) >= max(float(calc_result[1]), float(calc_result[2]))):  
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
        l_ex_price = str(h_price + float(tick_size))
        l_order_price = str(int(Decimal(l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_ex_qty = str((invest_usdt * float(l_sym_lever)) / float(l_order_price))
        l_order_qty = str(int(Decimal(l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        l_tp_ex_price = str(h_price + (limit_diff * 2) + float(tick_size))
        l_tp_price = str(int(Decimal(l_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_st_ex_price = str(h_price - limit_diff - float(tick_size))
        l_st_price = str(int(Decimal(l_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_order_side = 'Buy'
        l_order_position = 1
        l_ex_value = float(l_order_qty) * float(l_order_price) * 0.8

        s_ex_price = str(l_price + float(tick_size))
        s_order_price = str(int(Decimal(s_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_ex_qty = str((invest_usdt * float(s_sym_lever)) / float(s_order_price))
        s_order_qty = str(int(Decimal(s_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        s_tp_ex_price = str(l_price - (limit_diff * 2) - float(tick_size))
        s_tp_price = str(int(Decimal(s_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_st_ex_price = str(l_price + limit_diff + float(tick_size))
        s_st_price = str(int(Decimal(s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_order_side = 'Sell'
        s_order_position = 2
        s_ex_value = float(s_order_qty) * float(s_order_price) * 0.8
#-------------------------------------------------------------------------------
        if(long_qty == 0) and ((invest_usdt * 2) < avail_usdt) and (float(l_sym_lever) == float(calc_result[1])):
                if(order_result[0] == 11) and (float(max_lever) >= float(l_sym_lever)):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, 1, l_tp_price, l_st_price]
                    conditional_market_part(add_order)
                    time.sleep(1)

        if(short_qty == 0) and ((invest_usdt * 2) < avail_usdt) and (float(s_sym_lever) == float(calc_result[2])):
                if(order_result[0] == 11) and (float(max_lever) >= float(s_sym_lever)):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
  if(open_list != []):
    for sym_bol in open_list:
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
      status = instruments_info[0]['status']
#-------------------------------------------------------------------------------
      if(long_qty != 0):
          ex_act_price = str(float(l_ent_price) + (abs(float(l_ent_price) - float(l_st_loss))))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(l_trailing) == 0) and (float(act_price) > sym_price):
            ex_ts_diff = abs(float(l_ent_price) - float(l_st_loss)) * 1.0
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 1]
            set_trading_stop_item(add_order)
            time.sleep(1)
            opened_order_info = [sym_bol, 'L_open']
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message
#-------------------------------------------------------------------------------
      if(short_qty != 0):
          ex_act_price = str(float(s_ent_price) - (abs(float(s_ent_price) - float(s_st_loss))))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(s_trailing) == 0) and (float(act_price) < sym_price):
            ex_ts_diff = abs(float(s_ent_price) - float(s_st_loss)) * 1.0
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 2]
            set_trading_stop_item(add_order)
            time.sleep(1)
            opened_order_info = [sym_bol, 'S_open']
            url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={opened_order_info}"
            requests.get(url).json() # this sends the message
#-------------------------------------------------------------------------------
      if(sym_bol in Trail_list):
        session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')

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
#-------------------------------------------------------------------------------
  check_time = check_time + 1
  if(check_time == print_time):
    btc_info=session.get_tickers(category="linear",symbol='BTCUSDT')['result']['list']
    btc_price = float(pd.DataFrame(btc_info)['lastPrice'][0])
    url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'order_id_Equity = ',round(live_usdt,2), 'My Wallet = ', round(my_usdt,2),'BTCUSDT = ',btc_price}"
    requests.get(url).json() # this sends the message  max_usdt = live_usdt
    url = f"https://api.telegram.org/bot{order_id}/sendMessage?chat_id={chat_id}&text={'rest_list:',open_list}"
    requests.get(url).json() # this sends the message
    check_time = 0
###############################################################################
