#v5_test15-4-2_MAIN_JQ_260326-1000
#v5 api
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
##############################################################################
##############################################################################
kst = pytz.timezone("Asia/Seoul")
time_str = "2026-03-27,14:50"
dt = datetime.strptime(time_str, "%Y-%m-%d,%H:%M")
dt = kst.localize(dt)
start_time = int(dt.timestamp() * 1000)
##############################################################################
##############################################################################
chat_id = os.getenv("chat_id")
order_id = os.getenv("order_id")
session = HTTP(
    testnet=False,
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
    max_retries=10,
    retry_delay=15,
  )

invest_usdt = 2
delay_time = 60 #time_itv*60
check_time = 0
check_time1 = 0
return_time = 10
print_time = 300
first_time = int(time.time())
##############################################################################
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
  order_position = 0
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
    std_diff = c_list[0] * 0.5 / 5
    std_max = c_list[0] + std_diff
    std_min = c_list[0] - std_diff
    limit_diff = std_diff
    for fr in range(1,len(c_list)):
      fr_max = max(h_list[:fr])
      fr_min = min(l_list[:fr])
      if(fr_min <= std_min) and (fr_max < std_max): order_position = 1
      if(fr_max >= std_max) and (fr_min > std_min): order_position = 2
      if(order_position in (1, 2)): break
    xnum = h_list.index(fr_max)
    nnum = l_list.index(fr_min)
#-------------------------------------------------------------------------------
    if(fr_min <= std_min) and (fr_max >= std_max): break
    if(order_position not in (1, 2)): continue
#-------------------------------------------------------------------------------
  if(order_position == 1): l_next_price, s_next_price = c_list[0], std_min
  if(order_position == 2): l_next_price, s_next_price = std_max, c_list[0]
  mx_time = float(t_list[xnum] * 0.001)
  mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
  mn_time = float(t_list[nnum] * 0.001)
  mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
  s_value_list = [l_next_price, s_next_price]
  v_value_list = [itv, mx_server_time, mn_server_time]
#-------------------------------------------------------------------------------
  time.sleep(1)
  order_return = [order_position, limit_diff, s_value_list, v_value_list]
  return(order_return)
###############################################################################
################################################################################
def order_calc(sym_bol, start_time, order_side, ent_price, st_loss):
  sym_bol = order_value[0]
  order_side = order_value[1]
  ent_price = order_value[2]
  order_position = 0
#-------------------------------------------------------------------------------
  itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
  for itv in itv_list:
#-------------------------------------------------------------------------------
    now_time = int(time.time()) 
    if(now_time - (itv * 60 * 1000) > start_time): pass
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
      if(int(kline[0][i]) < start_time): break
#-------------------------------------------------------------------------------
    std_diff = ent_price * 0.5 / 5
    limit_diff = std_diff
    max_price, min_price = max(h_list), min(l_list)
    max_diff = max_price - min_price
    xnum = h_list.index(max_price)
    nnum = l_list.index(min_price)
    limit_st = abs(ent_price - st_loss) * 1.1)
    l_next_price, s_next_price = max_price, min_price
      
    if(order_side == 1):
      if(limit_st >= abs(ent_price - min_price)):
        order_position = 12
        l_next_price, s_next_price = ent_price - limit_st, min_price
      if(limit_st < abs(ent_price - min_price)):
        order_position = 32
        l_next_price, s_next_price = ent_price - st_loss, min_price
        if((ent_price - (std_diff * 2)) > min_price): order_position = 30

    if(order_side == 2):
      if(limit_st >= abs(ent_price - max_price)):
        order_position = 21
        l_next_price, s_next_price = max_price, ent_price - limit_st
      if(limit_st < abs(ent_price - max_price)):
        order_position = 41
        l_next_price, s_next_price = max_price, ent_price + st_loss
        if((ent_price + (std_diff * 2)) < max_price): order_position = 40
  
    mx_time = float(t_list[xnum] * 0.001)
    mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
    mn_time = float(t_list[nnum] * 0.001)
    mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
    s_value_list = [l_next_price, s_next_price]
    v_value_list = [itv, mx_server_time, mn_server_time]
    break
#-------------------------------------------------------------------------------
  time.sleep(1)
  order_return = [order_position, limit_diff, s_value_list, v_value_list]
  return(order_return)
#-------------------------------------------------------------------------------
###############################################################################
def calc_part(order_condition, sym_bol, h_price, l_price, std_diff):
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
    lever_point = h_price - std_diff
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
    lever_point = l_price + std_diff
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
start_time = int(time.time()) * 1000
check_symbol, check_order = [], []

while True:
  end_time = int(time.time())
  diff_time = end_time - start_time
  rest_time = int(150 - diff_time)
  if(140 > rest_time > 0): time.sleep(rest_time)
  start_time = int(time.time())
  wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
  my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
  live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
  tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
  time.sleep(1)
  avail_usdt = my_usdt - tot_position

  max_l_usdt, min_l_usdt, origin_usdt = live_usdt, live_usdt, my_usdt
  max_m_usdt, min_m_usdt = my_usdt, my_usdt
  max_t_position = tot_position

  try_item = []
  limit_max_num = my_usdt / invest_usdt
  limit_num = math.ceil(limit_max_num)
  if(limit_num > 200): limit_num = 200
  get_positions = pd.DataFrame(session.get_positions(category="linear",settleCoin="USDT",limit=limit_num)['result']['list'])
  time.sleep(1)
  if get_positions.empty: long_list, short_list = [], []
  else:
    long_list = get_positions[(get_positions['positionIdx'] == 1)]
    long_list = long_list['symbol'].unique().tolist()
    short_list = get_positions[(get_positions['positionIdx'] == 2)]
    short_list = short_list['symbol'].unique().tolist()
  union_list = list(set(long_list) | set(short_list))
  inter_list = list(set(long_list) & set(short_list))
  setdf_list = list(set(union_list) - set(inter_list))

  trail_list, take_list, stop_list = [], [], []
  for sym_bol in union_list:
    item_list = pd.DataFrame(session.get_open_orders(category="linear",symbol=sym_bol,orderFilter='StopOrder')['result']['list'])
    time.sleep(1)
    if item_list.empty: stop_type = []
    else: stop_type = item_list['stopOrderType'].unique().tolist()
    if('TakeProfit' in stop_type): take_list.append(sym_bol)
    if('TrailingStop' in stop_type): trail_list.append(sym_bol)
    if('Stop' in stop_type): stop_list.append(sym_bol)
    
  try_item = list((set(setdf_list) - set(trail_list)) | set(take_list))
  
  l_order_num = len(long_list)
  s_order_num = len(short_list)
  secure_item = len(union_list) - len(inter_list) - len(trail_list)
  secure_usdt = secure_item * invest_usdt
  avail_order_num = int(((avail_usdt - secure_usdt) / invest_usdt) * 0.5)
  
  cancel_list = list(set(trail_list) & set(stop_list))
  if(cancel_list != []):
    for sym_bol in cancel_list:
      session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#-------------------------------------------------------------------------------
  if(live_usdt > (my_usdt * 1.5)):
    for sym_bol in long_list:
      add_order = [sym_bol, "Sell", 1]
      closed_order_part(add_order)
      time.sleep(1)

    for sym_bol in short_list:
      add_order = [sym_bol, "Buy", 2]
      closed_order_part(add_order)
      time.sleep(1)

    avail_order_num = int((live_usdt / invest_usdt) * 0.5)
    union_list, try_item = [], []
    secure_usdt = 0
#-------------------------------------------------------------------------------
#rest_item = try_item.copy()
#-------------------------------------------------------------------------------
#  first_time = int(time.time())
#-------------------------------------------------------------------------------
# add item list
  ordered_item = 30
  #wish_item_no = 15
  wish_item_no = 100
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

    del_list = session.get_announcement(locale="en-US",type='Delistings',tag='Derivatives')['result']['list']
    if(del_list == []): title_list = []
    else: title_list = [item['title'] for item in del_list]
    all_words = []
    for title in title_list:
      all_words.extend(re.findall(r'\b\w+\b', title)) 
    uppercase_words = {word for word in all_words if word.isupper()}
    final_del_list = sorted(uppercase_words)
   
    added_symbols = [x for x in added_symbols if x not in union_list]
    added_symbols = [x for x in added_symbols if x not in final_del_list]
    added_symbols = [x for x in added_symbols if 'USDT' in x]
    time.sleep(1)
#-------------------------------------------------------------------------------
    if(check_symbol == []): 
      check_symbol = added_symbols.copy()
      for sym in range(len(check_symbol)): check_order.append(0)
   
    num = 0
    for sym_bol in added_symbols:
      search_calc_result = search_calc(sym_bol)   
      print(sym_bol, "check_order:", check_order[symbol_num], "serch_result:",search_calc_result)
      if(ordered_item > len(union_list)) and (check_order[symbol_num] != 0):
#        if(search_calc_result in (1, 2)) and (check_order[symbol_num] != search_calc_result):
        if(search_calc_result == 1) and (check_order[symbol_num] in (2, 20)):
          num = num + 1
          if(avail_order_num >= num): try_item.append(sym_bol)
        if(search_calc_result == 2) and (check_order[symbol_num] in (1, 10)):
          num = num + 1
          if(avail_order_num >= num): try_item.append(sym_bol)
      check_order[symbol_num] = search_calc_result
          
    cancel_symbol = list(set(check_symbol) - set(added_symbols))
    for sym_bol in cancel_symbol:
      symbol_num = check_symbol.index(sym_bol)
      check_order[symbol_num] = 0
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
  if(try_item != []):  
    last_time = int(time.time())
###############################################################################
    for sym_bol in try_item:
      item_no = try_item.index(sym_bol)
      i_last_time = int(time.time())
      now_time = int(time.time()) * 1000
      apply_time = start_time
###############################################################################
      sym_info=session.get_tickers(category="linear",symbol=sym_bol)['result']['list']
      time.sleep(1)
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

      wallet=session.get_wallet_balance(accountType="UNIFIED",coin="USDT")['result']['list']
      time.sleep(1)
      my_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['walletBalance'][0])
      avail_usdt = pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['availableToWithdraw'][0]
      live_usdt = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['equity'][0])
      tot_position = float(pd.DataFrame(pd.DataFrame(wallet)['coin'][0])['totalPositionIM'][0])
      if avail_usdt.strip(): avail_usdt = float(avail_usdt)
      else: avail_usdt = my_usdt - tot_position
#-------------------------------------------------------------------------------
      closed_pnl = pd.DataFrame(session.get_closed_pnl(category="linear", symbol=sym_bol, startTime=start_time)['result']['list'])
      if closed_pnl.empty: pnl_list_str, closed_time_str = [], []
      else: 
        pnl_list_str = closed_pnl['closedPnl'].tolist()
        pnl_list = [float(x) for x in pnl_list_str]
        closed_time_str = closed_pnl['createdTime'].tolist()
        closed_time = [int(x) for x in closed_time_str]

      order_history = pd.DataFrame(session.get_order_history(category="linear", symbol=sym_bol, orderFilter="Order", startTime=start_time)['result']['list'])
      if order_history.empty: open_time_str = []
      else:
        market_open_time = order_history[(order_history['orderType'] == "Market")]
        open_time_str = market_open_time['createdTime'].tolist()
        open_time = [int(x) for x in open_time_str]

      if(pnl_list != []) and (pnl_list[0] < 0):
          for clo in range(len(pnl_list)):
            if(pnl_list[clo] >= 0): break
          for opn in range(len(open_time)):
            if(closed_time[clo] > open_time[opn]):
              apply_time = open_time[opn]
              break 

      open_orders=session.get_open_orders(category="linear",symbol=sym_bol)['result']['list']
      if open_orders.empty: limit_order_list, stop_order_list = [], []
      else:
        limit_order_list = open_orders['orderType'].tolist()
        stop_order_list = open_orders['stopOrderType'].tolist()

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
  time.sleep(1)

            limit_order_list = open_orders['orderType'].tolist()
        stop_order_list = open_orders['stopOrderType'].tolist()
#-------------------------------------------------------------------------------
      order_condition[item_no] = 0
      if(long_qty == 0) and (short_qty == 0) and (("Limit" in limit_order_list) or ("Stop" in stop_order_list)):
        session.cancel_all_orders(category="linear", symbol=sym_bol)
        
      if(long_qty == 0) and (short_qty == 0):
          if(pnl_list == []) or ((pnl_list != []) and (pnl_list[0] > 0):
            search_calc_result = search_calc(sym_bol)
            order_condition[item_no] = search_calc_result[0]
            limit_diff_p[item_no] = search_calc_result[1]
            value_s_list[item_no] = search_calc_result[2]
            value_v_list[item_no] = search_calc_result[3]
          
      if("Limit" not in limit_order_list) and ("Stop" not in stop_order_list):
        if(long_qty != 0) and (short_qty == 0):
          order_calc_result = order_calc(sym_bol, apply_time, 1, float(l_ent_price), float(l_st_loss))
          order_condition[item_no] = order_calc_result[0]
          limit_diff_p[item_no] = order_calc_result[1]
          value_s_list[item_no] = order_calc_result[2]
          value_v_list[item_no] = order_calc_result[3]
            
        if(long_qty == 0) and (short_qty != 0):
          order_calc_result = order_calc(sym_bol, apply_time, 2, float(s_ent_price), float(s_st_loss))
          order_condition[item_no] = order_calc_result[0]
          limit_diff_p[item_no] = order_calc_result[1]
          value_s_list[item_no] = order_calc_result[2]
          value_v_list[item_no] = order_calc_result[3]

      h_price, l_price = value_s_list[item_no][1], value_s_list[item_no][2]
#-------------------------------------------------------------------------------
#START
#-------------------------------------------------------------------------------
      if(try_item != []):  
#-------------------------------------------------------------------------------
# order_calc
#        order_value = [sym_bol, sym_price, order_condition[item_no], limit_diff_p[item_no],
#                       value_s_list[item_no], value_v_list[item_no]]
#        order_calc_result = order_calc(order_value)
#-------------------------------------------------------------------------------
# order_calc_result
#        order_condition[item_no] = order_calc_result[0]
#        limit_diff_p[item_no] = order_calc_result[1]
#        value_s_list[item_no] = order_calc_result[2]
#        value_v_list[item_no] = order_calc_result[3]
#-------------------------------------------------------------------------------
        apply_lever = "5"
        if(float(apply_lever) > float(min_lever)): pass
        if(long_qty == 0) and (short_qty == 0):
            if(float(apply_lever) != float(l_sym_lever)) or (float(apply_lever) != float(s_sym_lever)):
              session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=apply_lever, sellLeverage=apply_lever)
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
#        h_price, l_price = sym_price, sym_price
#        h_price, l_price = value_s_list[item_no][1], value_s_list[item_no][2]
#-------------------------------------------------------------------------------
# calc_part_result
# calc_return = [sym_bol, l_new_lever, s_new_lever]
#        calc_result = calc_part(order_condition[item_no], sym_bol, h_price, l_price, limit_diff_p[item_no])
#-------------------------------------------------------------------------------
#        if(float(max_lever) >= max(float(calc_result[1]), float(calc_result[2]))) and (order_condition[item_no] in (1, 2)):  
#          if(long_qty == 0) and (short_qty == 0):
#            if(float(calc_result[1]) != float(l_sym_lever)) or (float(calc_result[2]) != float(s_sym_lever)):
#              session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=calc_result[1], sellLeverage=calc_result[2])
#              time.sleep(1)
#          if(long_qty == 0) and (short_qty != 0) and (float(calc_result[1]) != float(l_sym_lever)):
#              session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=calc_result[1], sellLeverage=s_sym_lever)
#              time.sleep(1)
#          if(long_qty != 0) and (short_qty == 0) and (float(calc_result[2]) != float(s_sym_lever)):
#              session.set_leverage(category="linear", symbol=sym_bol, buyLeverage=l_sym_lever, sellLeverage=calc_result[2])
#              time.sleep(1)
#
#        res_ponse=session.get_positions(category="linear",symbol=sym_bol)['result']['list']
#        time.sleep(1)
#        position_idx = pd.DataFrame(res_ponse)['positionIdx'][0]
#        if(position_idx == 1):
#          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
#          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
#        else:
#          l_sym_lever = pd.DataFrame(res_ponse)['leverage'][1]
#          s_sym_lever = pd.DataFrame(res_ponse)['leverage'][0]
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
        if(float(s_tp_ex_price) < (l_price * 0.15)): s_tp_ex_price = str(l_price * 0.15)
        s_tp_price = str(int(Decimal(s_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_st_ex_price = str(l_price + limit_diff_p[item_no] + float(tick_size))
        s_st_price = str(int(Decimal(s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_order_side = 'Sell'
        s_order_position = 2
        s_ex_value = float(s_order_qty) * float(s_order_price) * 1.0
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#        if(m_order_idx[1] == 1):
#            if(m_order_st[1] >= sym_price):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#
#            if(l_avail_num <= 0):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#         
#        if(m_order_idx[2] == 2):
#            if(m_order_st[2] <= sym_price):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#            
#            if(s_avail_num <= 0):
#              session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#-------------------------------------------------------------------------------
        if(order_condition[item_no] != 0):
            ("Limit" not in limit_order_list) and ("Stop" not in stop_order_list)
#-------------------------------------------------------------------------------
          if(order_condition[item_no] == 1):
            if(long_qty == 0) and ((invest_usdt * 2) < avail_usdt):
                if(float(max_lever) >= float(l_sym_lever)):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_tp_price, l_st_price]
                    order_market_part(add_order)
                    time.sleep(1)
                if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)

          if(order_condition[item_no] == 2):
            if(short_qty == 0) and ((invest_usdt * 2) < avail_usdt):
                if(float(max_lever) >= float(s_sym_lever)):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_tp_price, s_st_price]                  
                    order_market_part(add_order)
                    time.sleep(1)
                if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, l_order_price, 1, l_tp_price, l_st_price]
                    conditional_market_part(add_order)
                    time.sleep(1)

          if(long_qty != 0) and ((invest_usdt * 1) < avail_usdt):
            if(order_condition[item_no] in (30, 32)) and ("Limit" not in limit_order_list):
                if(float(max_lever) >= float(l_sym_lever)):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, l_order_price, 1, l_tp_price, l_st_price]
                    order_limit_part(add_order)
                    time.sleep(1)
            if(order_condition[item_no] in (12, 32) and ("Stop" not in stop_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
            if(order_condition[item_no] == 12):
                    add_order = [sym_bol, l_order_price, 1]                  
                    set_stop_loss_item(add_order)

          if(short_qty != 0) and ((invest_usdt * 2) < avail_usdt):
            if(order_condition[item_no] in (40, 41)) and ("Limit" not in limit_order_list):
                if(float(max_lever) >= float(s_sym_lever)):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    order_limit_part(add_order)
                    time.sleep(1)
            if(order_condition[item_no] in (21, 41) and ("Stop" not in stop_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, l_order_price, 1, l_tp_price, l_st_price]
                    conditional_market_part(add_order)
                    time.sleep(1)
            if(order_condition[item_no] == 21):
                    add_order = [sym_bol, s_order_price, 2]                  
                    set_stop_loss_item(add_order)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(long_qty != 0):
          ex_act_price = str(float(l_ent_price) + (abs(float(l_ent_price) - float(l_st_loss)) * 1.0))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(l_trailing) == 0) and (float(act_price) > sym_price):
            ex_ts_diff = abs(float(l_ent_price) - float(l_st_loss)) * 1.0
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 1]
            set_trading_stop_item(add_order)
#-------------------------------------------------------------------------------
        if(short_qty != 0):
          ex_act_price = str(float(s_ent_price) - (abs(float(s_ent_price) - float(s_st_loss)) * 1.0))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(s_trailing) == 0) and (float(act_price) < sym_price):
            ex_ts_diff = abs(float(s_ent_price) - float(s_st_loss)) * 1.0
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 2]
            set_trading_stop_item(add_order)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(long_qty != 0):
          if(float(l_position_im) > (invest_usdt * 1.5)):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'Over_order_L_closed'
            opened_order_info = [sym_bol, pre_condition[item_no], order_condition[item_no], round(float(l_position_im),1)]

        if(short_qty != 0):
          if(float(s_position_im) > (invest_usdt * 1.5)):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            order_condition[item_no] = 'Over_order_S_closed'
            opened_order_info = [sym_bol, pre_condition[item_no], order_condition[item_no], round(float(s_position_im),1)]
###############################################################################
        if(long_qty != 0) and (short_qty != 0):
          print(sym_bol,sym_price,'order_condition:',order_condition[item_no],'l_unpnl:',l_unpnl,'s_unpnl:',s_unpnl)
        elif(long_qty == 0) and (short_qty != 0):
          print(sym_bol,sym_price,'order_condition:',order_condition[item_no],'s_unpnl:',s_unpnl)
        elif(long_qty != 0) and (short_qty == 0):
          print(sym_bol,sym_price,'order_condition:',order_condition[item_no],'l_unpnl:',l_unpnl)
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
      check_time1 = 0
#    if(check_time >= return_time):
#      check_time = 0
#      break
###############################################################################
  korea_tz = pytz.timezone('Asia/Seoul')
  current_time_korea = datetime.now(korea_tz)
  current_time = current_time_korea.strftime('%Y-%m-%d %H:%M:%S')
  print('Live_USDT: ', round(live_usdt,2), 'My_USDT: ', round(my_usdt,2))
  print("Secure_usdt:", secure_usdt, "Avail_usdt:", round(avail_usdt,2),'invest_USDT:',round(invest_usdt,1))
  print("Avail_num:", avail_order_num, "L_num:", l_order_num, "S_num:", s_order_num, "Try_num:", len(try_item))    
#    print('m_USDT_MAX_MIN :',round(max_m_usdt,2),round(min_m_usdt,2),'my_USDT: ',round(my_usdt,2),'origin_usdt:',round(origin_usdt,2))
#    print('T_POSITION_MAX_NOW :',round(max_t_position,2),round(tot_position,2),'invest_USDT:',round(invest_usdt,1))
  print(current_time,'Reset')
