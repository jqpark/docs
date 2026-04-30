#v5_test15-5-7_MAINJQ_260422-1630_61.0_0424-1700_92.4
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

invest_usdt = 2
check_order_list = []
##############################################################################
##############################################################################
kst = pytz.timezone("Asia/Seoul")
time_str = "2026-04-22,16:30"
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
chat_id = os.getenv("chat_id")
order_id = os.getenv("order_id")
session = HTTP(
    testnet=False,
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
    max_retries=10,
    retry_delay=15,
  )
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
def set_trading_stop_profit(add_order):
      print(session.set_trading_stop(
            category="linear",
            symbol=add_order[0],
            takeProfit="0",
            trailingStop=add_order[1],
            tpslMode="Full",
            positionIdx=add_order[2],
))
################################################################################
################################################################################
def search_calc(sym_bol):
  order_position = 9
  itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]
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
    cal_lever, order_position = 5, 9
    fr_vol, bk_vol, std_vol = 0, 0, 0
    upp_lever, low_lever = 0, 0
    std_diff = c_list[0] * 0.5 / 5
    limit_diff = std_diff
    upp_max, low_min = max(h_list), min(l_list)
    l_next_price, s_next_price = upp_max, low_min
    max_diff = upp_max - low_min
    xnum = h_list.index(upp_max)
    nnum = l_list.index(low_min)
    max_vol = sum(v_list[min(nnum,xnum):max(nnum,xnum)+1])
    max_avg = max_vol / max_diff

    diff_range = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    for diff in diff_range:
      if(max_diff > (std_diff * diff)):
        std_vol = max_avg * (std_diff * diff)
        for fr in range(1,len(c_list)):
          fr_vol = sum(v_list[:fr])
          if(fr_vol > std_vol):
            fr_max = max(h_list[:fr])
            fr_min = min(l_list[:fr])
            fr_diff = fr_max - fr_min
            fr_xnum = h_list[:fr].index(fr_max)
            fr_nnum = l_list[:fr].index(fr_min)
            break
#-------------------------------------------------------------------------------
        if(fr_vol <= std_vol): continue
#-------------------------------------------------------------------------------
        for bk in range(fr,len(v_list)):
          bk_vol = sum(v_list[fr:bk])
          if(bk_vol > std_vol):
            bk_max = max(h_list[fr:bk])
            bk_min = min(l_list[fr:bk])
            bk_diff = bk_max - bk_min
            bk_xnum = h_list[fr:bk].index(bk_max) + fr
            bk_nnum = l_list[fr:bk].index(bk_min) + fr
            break
#-------------------------------------------------------------------------------
        if(bk_vol <= std_vol): continue
#-------------------------------------------------------------------------------
        upp_max, low_min = max(fr_max, bk_max), min(fr_min, bk_min)  
        order_position = 9
        if(o_list[fr] < c_list[0]):
          order_position = 11
          cal_diff = abs(c_list[0] - low_min)
          if(cal_diff == 0): cal_lever = 100
          else: cal_lever = round(c_list[0] * 0.5 / cal_diff,2)
          limit_diff = cal_diff
        if(o_list[fr] > c_list[0]):
          order_position = 22
          cal_diff = abs(c_list[0] - upp_max)
          if(cal_diff == 0): cal_lever = 100
          else: cal_lever = round(c_list[0] * 0.5 / cal_diff,2)
          limit_diff = cal_diff
            
        c_selection = 0
        if(cal_lever <= 10) and (cal_lever >= 5): c_selection = 9
        if(order_position == 11) and (c_selection == 9): order_position = 1
        if(order_position == 22) and (c_selection == 9): order_position = 2
        if(cal_lever > 10): continue
        break
    if(cal_lever > 10): continue
    if(min(fr_vol, bk_vol) > std_vol): break
#-------------------------------------------------------------------------------
  if(order_position == 1): l_next_price, s_next_price = c_list[0], low_min
  if(order_position == 2): l_next_price, s_next_price = upp_max, c_list[0]
  mx_time = float(t_list[xnum] * 0.001)
  mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
  mn_time = float(t_list[nnum] * 0.001)
  mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
  s_value_list = [l_next_price, s_next_price, cal_lever]
  v_value_list = [itv, mx_server_time, mn_server_time]
#-------------------------------------------------------------------------------
  order_return = [order_position, limit_diff, s_value_list, v_value_list]
  return(order_return)
###############################################################################
################################################################################
def order_calc(sym_bol, apply_time, order_side, ent_price, st_loss, sym_lever, stop_condition):
  order_position = 9
#-------------------------------------------------------------------------------
  itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
  for itv in itv_list:
#-------------------------------------------------------------------------------
    now_time = int(time.time())
    cal_time = (now_time - (itv * 60 * 1000)) * 1000
    if(cal_time > apply_time): continue
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
      if(int(kline[0][i]) < apply_time): break
#-------------------------------------------------------------------------------
    std_diff = ent_price * 0.5 / 5
    st_gap = abs(ent_price - st_loss)
    limit_diff = st_gap
    calc_max, calc_min = max(h_list), min(l_list)
    max_diff = calc_max - calc_min
    xnum = h_list.index(calc_max)
    nnum = l_list.index(calc_min)
    max_price = max((ent_price + st_gap), calc_max)
    min_price = min((ent_price - st_gap), calc_min)
    l_next_price, s_next_price = max_price, min_price
      
    if(stop_condition == 0):
      if(order_side == 1):
        order_position = 12
        l_next_price, s_next_price = calc_min + st_gap, calc_min
      if(order_side == 2):
        order_position = 21
        l_next_price, s_next_price = calc_max, calc_max - st_gap
      
    if(stop_condition == 1):
      if(order_side == 1):
        if((ent_price - st_gap) > min_price):
          order_position = 30
          l_next_price, s_next_price = ent_price - st_gap, min_price

      if(order_side == 2):
        if((ent_price + st_gap) < max_price):
          order_position = 40
          l_next_price, s_next_price = max_price, ent_price + st_gap

      if(order_side == 3):
        l_next_price, s_next_price = c_list[0] + st_gap, c_list[0]
        if((c_list[0] + (st_gap * 0.0)) < ent_price):
          order_position = 32
      if(order_side == 4):
        l_next_price, s_next_price = c_list[0], c_list[0] - st_gap
        if((c_list[0] - (st_gap * 0.0)) > ent_price):
          order_position = 41
      
    mx_time = float(t_list[xnum] * 0.001)
    mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
    mn_time = float(t_list[nnum] * 0.001)
    mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
    s_value_list = [l_next_price, s_next_price, calc_max, calc_min]
    v_value_list = [itv, mx_server_time, mn_server_time]
    break
#-------------------------------------------------------------------------------
  order_return = [order_position, limit_diff, s_value_list, v_value_list]
  return(order_return)
#-------------------------------------------------------------------------------
################################################################################
def recycle_calc(sym_bol, apply_time):
  order_position = 9
#-------------------------------------------------------------------------------
  itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
  for itv in itv_list:
#-------------------------------------------------------------------------------
    now_time = int(time.time())
    cal_time = (now_time - (itv * 60 * 1000)) * 1000
    if(cal_time > apply_time): continue
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
      if(int(kline[0][i]) < apply_time): break
#-------------------------------------------------------------------------------
    std_diff = c_list[0] * 0.5 / 5
    limit_diff = std_diff
    max_price, min_price = max(h_list), min(l_list)
    max_diff = max_price - min_price
    xnum = h_list.index(max_price)
    nnum = l_list.index(min_price)
    l_next_price, s_next_price = max_price, min_price
      
    mx_time = float(t_list[xnum] * 0.001)
    mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
    mn_time = float(t_list[nnum] * 0.001)
    mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
    s_value_list = [l_next_price, s_next_price]
    v_value_list = [itv, mx_server_time, mn_server_time]
    break
#-------------------------------------------------------------------------------
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
while True:
  wallet = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")['result']['list']
  coin_info = wallet[0]['coin'][0]
  my_usdt = float(coin_info['walletBalance'])
  live_usdt = float(coin_info['equity'])
  tot_position = float(coin_info['totalPositionIM'])
  total_order_im = float(coin_info['totalOrderIM'])
  avail_usdt = my_usdt - (tot_position + total_order_im)
  time.sleep(1)

  max_l_usdt, min_l_usdt, origin_usdt = live_usdt, live_usdt, my_usdt
  max_m_usdt, min_m_usdt = my_usdt, my_usdt
  max_t_position = tot_position

  try_item = []
  union_list, inter_list, setdf_list = [], [], []
  limit_max_num = my_usdt / invest_usdt
  limit_num = math.ceil(limit_max_num)
  if(limit_num > 200): limit_num = 200
  limit_num = 200
  get_positions = pd.DataFrame(session.get_positions(category="linear",settleCoin="USDT",limit=limit_num)['result']['list'])
  time.sleep(1)
  if get_positions.empty: long_list, short_list = [], []
  else:
    long_list = get_positions[(get_positions['positionIdx'] == 1)]
    long_list = long_list['symbol'].unique().tolist()
    short_list = get_positions[(get_positions['positionIdx'] == 2)]
    short_list = short_list['symbol'].unique().tolist()
    union_list = get_positions['symbol'].unique().tolist()

#  trail_list, take_list, stop_list = [], [], []
#  for sym_bol in union_list:
#    item_list = pd.DataFrame(session.get_open_orders(category="linear",symbol=sym_bol,orderFilter='StopOrder')['result']['list'])
#    time.sleep(1)
#    if item_list.empty: stop_type = []
#    else: stop_type = item_list['stopOrderType'].unique().tolist()
#    if('TakeProfit' in stop_type): take_list.append(sym_bol)
#    if('TrailingStop' in stop_type): trail_list.append(sym_bol)
#    if('Stop' in stop_type): stop_list.append(sym_bol)
    
  try_list = union_list.copy()
#-------------------------------------------------------------------------------
  all_orders = []
  cursor = None
  while True:
    res = session.get_open_orders(category="linear", settleCoin="USDT", orderFilter='StopOrder', limit=50, cursor=cursor)
    data = res["result"]["list"]
    all_orders.extend(data)
    cursor = res["result"]["nextPageCursor"]
    if not cursor: break
  open_orders = pd.DataFrame(all_orders)
  time.sleep(1)
  if open_orders.empty: check_order_list = []
  else: check_order_list = open_orders['symbol'].unique().tolist()
  print('check_order_list:',len(check_order_list))
#  check_order_list = [x for x in check_order_list if x not in try_list]
#  if(check_order_list != []): try_list.extend(check_order_list)
    
#  if(check_order_list == []):
#    check_list = pd.DataFrame(session.get_open_orders(category="linear",settleCoin="USDT",orderFilter='StopOrder',limit=50)['result']['list'])
#    time.sleep(1)
#    if check_list.empty: check_order_list = []
#    else: check_order_list = check_list['symbol'].unique().tolist()
#  print('try_list:',len(try_list),'check_order_list:',len(check_order_list))

  for sym_bol in check_order_list:
    if(sym_bol not in try_list):
      closed_pnl = pd.DataFrame(session.get_closed_pnl(category="linear", symbol=sym_bol, startTime=start_time, limit=1)['result']['list'])
      if closed_pnl.empty: last_pnl = 0
      else: last_pnl = float(closed_pnl['closedPnl'][0])
      time.sleep(1)
      if(last_pnl < 0):
        try_list.append(sym_bol)
      if(last_pnl > 0):
        check_order_list.remove(sym_bol)
        session.cancel_all_orders(category="linear", symbol=sym_bol)
  for sym_bol in try_list:
    if(sym_bol not in check_order_list): check_order_list.append(sym_bol)
#-------------------------------------------------------------------------------
  l_order_num = len(long_list)
  s_order_num = len(short_list)
  secure_usdt = max(l_order_num, s_order_num) * invest_usdt * 0.5
  avail_order_num = int((avail_usdt - secure_usdt) / (invest_usdt * 3))
#-------------------------------------------------------------------------------
#  first_time = int(time.time())
#-------------------------------------------------------------------------------
# add item list
  ordered_item = 20
  #wish_item_no = 15
  wish_item_no = 100
  if(avail_order_num > 0) and (ordered_item > len(try_list)):
    tickers = session.get_tickers(category="linear")['result']['list']
    df = pd.DataFrame(tickers)
    df['turnover24h'] = df['turnover24h'].astype(float)
    df['lastPrice'] = df['lastPrice'].astype(float)
    df['price24hPcnt'] = df['price24hPcnt'].astype(float)
    sort_list = df.sort_values('price24hPcnt', key=lambda x: x.abs(), ascending=False, ignore_index=True)
    added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2)) & (sort_list['turnover24h'] > 3e7)]
#  added_list = sort_list[(sort_list['lastPrice'] > 0.01) & (sort_list['lastPrice'] < 2) & (sort_list['turnover24h'] > 3e+07)]
#  added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
    added_symbols = added_list["symbol"].tolist()

    del_list = session.get_announcement(locale="en-US",type='Delistings',tag='Derivatives')['result']['list']
    if(del_list == []): title_list = []
    else: title_list = [item['title'] for item in del_list]
    all_words = []
    for title in title_list:
      all_words.extend(re.findall(r'\b\w+\b', title)) 
    uppercase_words = {word for word in all_words if word.isupper()}
    final_del_list = sorted(uppercase_words)
   
    added_symbols = [x for x in added_symbols if x not in try_list]
    added_symbols = [x for x in added_symbols if x not in final_del_list]
    added_symbols = [x for x in added_symbols if 'USDT' in x]
    time.sleep(1)
    print('added_symbols:',len(added_symbols))

    added_symbol_list = []
    for sym_bol in added_symbols:
      closed_pnl = pd.DataFrame(session.get_closed_pnl(category="linear", symbol=sym_bol, startTime=start_time, limit=1)['result']['list'])
      if closed_pnl.empty: last_pnl = 0
      else: last_pnl = float(closed_pnl['closedPnl'][0])
      time.sleep(1)
      if(last_pnl >= 0): added_symbol_list.append(sym_bol)
    if(added_symbol_list != []): try_list.extend(added_symbol_list)
    print('added_symbol_list:',len(added_symbol_list))
#-------------------------------------------------------------------------------
#  try_list.extend(added_symbols)
  try_item = try_list.copy()
  print('try_item:',len(try_item))
#  if("GUNUSDT" not in try_item): try_item.append("GUNUSDT")
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
    num = 0
#    print(session.get_server_time())  
###############################################################################
    for sym_bol in try_item:
      item_no = try_item.index(sym_bol)
      i_last_time = int(time.time())
      now_time = int(time.time()) * 1000
      apply_time = start_time
###############################################################################
      sym_info=session.get_tickers(category="linear",symbol=sym_bol)['result']['list']
#      time.sleep(1)
      sym_price = float(pd.DataFrame(sym_info)['lastPrice'][0])

      res = session.get_executions(category="linear", symbol=sym_bol, execType="Trade", limit=10)
      if res.get("retCode") != 0:
        print("execution API error:", res.get("retMsg"))
        created_time, exec_price, trade_side, trade_type = 0, 0, 0, "None"
        continue
      else:
        last_trade = pd.DataFrame(res.get("result", {}).get("list", []))
        if last_trade.empty: created_time, exec_price, trade_side = 0, 0, 0
        else:
          last_trade = last_trade.sort_values("execTime", ascending=False)
          created_time = int(last_trade.iloc[0]["execTime"])
          exec_price = float(last_trade.iloc[0]["execPrice"])
          trade_side = last_trade.iloc[0]["side"]
          trade_type = str(last_trade.iloc[0]["stopOrderType"])
#      time.sleep(1)
      res_ponse = session.get_positions(category="linear", symbol=sym_bol)['result']['list']
      df = pd.DataFrame(res_ponse)
#-------------------------------------------------------------------------------
      def clean(x):
        if x is None or str(x).strip() == "":
          return 0
        return x
#-------------------------------------------------------------------------------
      position_idx = df['positionIdx'][0]
      if position_idx == 1: l_idx, s_idx = 0, 1
      else: l_idx, s_idx = 1, 0
      long_qty = float(df['size'][l_idx])
      short_qty = float(df['size'][s_idx])
      l_sym_lever = df['leverage'][l_idx]
      s_sym_lever = df['leverage'][s_idx]
      l_ent_price = df['avgPrice'][l_idx]
      s_ent_price = df['avgPrice'][s_idx]
      l_unpnl = df['unrealisedPnl'][l_idx]
      s_unpnl = df['unrealisedPnl'][s_idx]
      l_position = df['positionBalance'][l_idx]
      s_position = df['positionBalance'][s_idx]
      l_st_loss = clean(df['stopLoss'][l_idx])
      s_st_loss = clean(df['stopLoss'][s_idx])
      l_trailing = clean(df['trailingStop'][l_idx])
      s_trailing = clean(df['trailingStop'][s_idx])
      l_trade_mode = df['tradeMode'][l_idx]
      s_trade_mode = df['tradeMode'][s_idx]
      l_position_im = clean(df['positionIM'][l_idx])
      s_position_im = clean(df['positionIM'][s_idx])
      l_created_time = clean(df['updatedTime'][l_idx])
      s_created_time = clean(df['updatedTime'][s_idx])
      l_liq_price = clean(df['liqPrice'][l_idx])
      s_liq_price = clean(df['liqPrice'][s_idx])

      instruments_info = session.get_instruments_info(category="linear", symbol=sym_bol)['result']['list']
      info = instruments_info[0]
      qty_step = info['lotSizeFilter']['qtyStep']
      min_value = info['lotSizeFilter']['minNotionalValue']
      min_qty = info['lotSizeFilter']['minOrderQty']
      tick_size = info['priceFilter']['tickSize']
      max_lever = info['leverageFilter']['maxLeverage']
      min_lever = info['leverageFilter']['minLeverage']
      lever_step = info['leverageFilter']['leverageStep']
      status = info['status']

      wallet = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")['result']['list']
      coin_info = wallet[0]['coin'][0]
      my_usdt = float(coin_info['walletBalance'])
      live_usdt = float(coin_info['equity'])
      tot_position = float(coin_info['totalPositionIM'])
      total_order_im = float(coin_info['totalOrderIM'])
      avail_usdt = my_usdt - (tot_position + total_order_im)
#-------------------------------------------------------------------------------
# closed pnl 조회
      res_pnl = session.get_closed_pnl(category="linear", symbol=sym_bol, startTime=apply_time)
      if res_pnl.get("retCode") != 0:
        print("closed_pnl API error:", res_pnl.get("retMsg"))
        continue
      else: closed_pnl = pd.DataFrame(res_pnl["result"]["list"])
      if closed_pnl.empty:
        last_pnl = 0
        closed_time, closed_side, closed_pnl, pnl_list = [], [], [], []
      else:
        closed_pnl = closed_pnl.sort_values("updatedTime", ascending=False)
        last_pnl = float(closed_pnl.iloc[0]["closedPnl"])
        closed_time = closed_pnl["updatedTime"].astype(int).tolist()
        closed_side_str = closed_pnl["side"].tolist()
        pnl_list = closed_pnl["closedPnl"].astype(float).tolist()
              
# order history 조회
      res_order = session.get_order_history(category="linear", symbol=sym_bol, startTime=apply_time)
      if res_order.get("retCode") != 0:
        print("order_history API error:", res_order.get("retMsg"))
        continue
      else:
        order_history = pd.DataFrame(res_order["result"]["list"])
        if order_history.empty:
          open_time, rev_open_time,open_side = [], [], []
        else:
          stop_type = order_history["stopOrderType"].fillna("")
          order_type = order_history["orderType"].fillna("")
          order_open = order_history[
                       (((order_type.isin(["Market","Limit"])) & (stop_type == "")) | (stop_type == "Stop"))
                       & (order_history["reduceOnly"] == False)
                       & (order_history["orderStatus"].isin(["Filled","PartiallyFilled"]))
                       ]
          order_open = order_open.sort_values("updatedTime", ascending=False)
          open_time = order_open["updatedTime"].astype(int).tolist()
          open_side = order_open["side"].tolist()
          rev_open_time = list(reversed(open_time))
        
      accum_pnl, accum_num, accum_list = 0, 0, 0
      if(pnl_list != []):
        for clo in range(len(pnl_list)):
          if(pnl_list[clo] >= 0): break
        if(pnl_list[clo] < 0):
          apply_time = rev_open_time[0]
          accum_pnl = sum(pnl_list[:(clo + 1)])
          accum_list = pnl_list[:(clo + 1)]
          accum_num = open_time.index(rev_open_time[0])
        else:
          for opn in range(len(rev_open_time)):
            if(closed_time[clo] < rev_open_time[opn]):
              apply_time = rev_open_time[opn]
              break
          if(apply_time != rev_open_time[opn]): accum_pnl, accum_list, accum_num = 0, 0, 0
          else:
            accum_pnl = sum(pnl_list[:clo])
            accum_list = pnl_list[:clo]
            accum_num = open_time.index(apply_time)
      if(accum_pnl >= 0): apply_time = created_time
      if(pnl_list == []): clo = 0
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------        
      m_order_idx, m_order_tp, m_order_st, m_order_qty = [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]         
      open_orders = pd.DataFrame(session.get_open_orders(category="linear",symbol=sym_bol)['result']['list'])
      if open_orders.empty:
         limit_order_list = []
         stop_order_list = []
         trail_item = 0
      else:
        limit_order_list = open_orders['orderType'].tolist()
        stop_order_list = open_orders['stopOrderType'].tolist()
        if('TrailingStop' in stop_order_list): trail_item = 1
        else: trail_item = 0

        stop_df = open_orders[open_orders["stopOrderType"] == "Stop"]
        if not stop_df.empty:
            long_row = stop_df[stop_df["positionIdx"] == 1]
            short_row = stop_df[stop_df["positionIdx"] == 2]
            if not long_row.empty:
              m_order_idx[1] = 1
              m_order_tp[1] = float(long_row.iloc[0]["triggerPrice"])
              m_order_st[1] = float(long_row.iloc[0]["stopLoss"])
              m_order_qty[1] = float(long_row.iloc[0]["qty"])
            if not short_row.empty:
              m_order_idx[2] = 2
              m_order_tp[2] = float(short_row.iloc[0]["triggerPrice"])
              m_order_st[2] = float(short_row.iloc[0]["stopLoss"])
              m_order_qty[2] = float(short_row.iloc[0]["qty"])      
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
      if(long_qty != 0) and (short_qty != 0) and (trade_side != 0):
        if(trade_side == 'Sell') and (trade_type == 'Stop'):
          add_order = [sym_bol, "Sell", 1]
          closed_order_part(add_order)
          print(sym_bol, "S_Stop_open, L_closed")
          time.sleep(1)
        if(trade_side == 'Buy') and (trade_type == 'Stop'):
          add_order = [sym_bol, "Buy", 2]
          closed_order_part(add_order)
          print(sym_bol, "L_Stop_open, S_closed")
          time.sleep(1)
        continue
#-------------------------------------------------------------------------------
      if(long_qty != 0) and (float(l_liq_price) > max(float(l_st_loss), m_order_tp[2])):
        if(float(l_liq_price) != 0) and (float(l_st_loss) != 0) and (m_order_tp[2] != 0):
          add_order = [sym_bol, "Sell", 1]
          closed_order_part(add_order)
          time.sleep(1)
          print(sym_bol, "l_liq_price_closed","l_liq:",float(l_liq_price), "l_st_loss:",float(l_st_loss), "m_order_tp[2]:", m_order_tp[2])
          session.cancel_all_orders(category="linear", symbol=sym_bol)
          continue
      if(short_qty != 0) and (float(s_liq_price) < min(float(s_st_loss), m_order_tp[1])):
        if(float(s_liq_price) != 0) and (float(s_st_loss) != 0) and (m_order_tp[1] != 0):
          add_order = [sym_bol, "Buy", 2]
          closed_order_part(add_order)
          time.sleep(1)
          print(sym_bol, "s_liq_price_closed","s_liq:",float(s_liq_price), "s_st_loss:",float(s_st_loss), "m_order_tp[2]:", m_order_tp[1])
          session.cancel_all_orders(category="linear", symbol=sym_bol)
          continue
#-------------------------------------------------------------------------------        
#-------------------------------------------------------------------------------        
      if(trail_item == 1):
        if("Limit" in limit_order_list):
          session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='Order')
        if("Stop" in stop_order_list):
          session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
#-------------------------------------------------------------------------------
      if(long_qty == 0) and (short_qty == 0):
          if(pnl_list == []) or ((pnl_list != []) and (pnl_list[0] > 0)):
            search_calc_result = search_calc(sym_bol)
            order_condition[item_no] = search_calc_result[0]
            limit_diff_p[item_no] = search_calc_result[1]
            value_s_list[item_no] = search_calc_result[2]
            value_v_list[item_no] = search_calc_result[3]
            if(order_condition[item_no] in (1, 2)): num = num + 1
          
      if("Stop" not in stop_order_list) and (trail_item == 0) and (sym_bol in union_list):
        stop_condition = 0  
        if(long_qty != 0) and (short_qty == 0):
          order_calc_result = order_calc(sym_bol, apply_time, 1, exec_price, float(l_st_loss), float(l_sym_lever), stop_condition)
        if(long_qty == 0) and (short_qty != 0):
          order_calc_result = order_calc(sym_bol, apply_time, 2, exec_price, float(s_st_loss), float(s_sym_lever), stop_condition)
        order_condition[item_no] = order_calc_result[0]
        limit_diff_p[item_no] = order_calc_result[1]
        value_s_list[item_no] = order_calc_result[2]
        value_v_list[item_no] = order_calc_result[3]
            
      if("Stop" in stop_order_list) and ("Limit" not in limit_order_list) and (trail_item == 0):
        stop_condition = 1  
        if(long_qty != 0) and (short_qty == 0):
          order_calc_result = order_calc(sym_bol, apply_time, 1, exec_price, float(l_st_loss), float(l_sym_lever), stop_condition)
        if(long_qty == 0) and (short_qty != 0):
          order_calc_result = order_calc(sym_bol, apply_time, 2, exec_price, float(s_st_loss), float(s_sym_lever), stop_condition)
        if(long_qty == 0) and (short_qty == 0) and (pnl_list != []) and (pnl_list[0] < 0):
          if(m_order_idx[1] == 1):
            order_calc_result = order_calc(sym_bol, apply_time, 3, m_order_tp[1], m_order_st[1], float(l_sym_lever), stop_condition)
          if(m_order_idx[2] == 2):
            order_calc_result = order_calc(sym_bol, apply_time, 4, m_order_tp[2], m_order_st[2], float(s_sym_lever), stop_condition)
        order_condition[item_no] = order_calc_result[0]
        limit_diff_p[item_no] = order_calc_result[1]
        value_s_list[item_no] = order_calc_result[2]
        value_v_list[item_no] = order_calc_result[3]
           
      if(order_condition[item_no] == 0):
          recycle_calc_result = recycle_calc(sym_bol, apply_time)
          order_condition[item_no] = recycle_calc_result[0]
          limit_diff_p[item_no] = recycle_calc_result[1]
          value_s_list[item_no] = recycle_calc_result[2]
          value_v_list[item_no] = recycle_calc_result[3]
      h_price, l_price = value_s_list[item_no][0], value_s_list[item_no][1]
#-------------------------------------------------------------------------------
#START
#-------------------------------------------------------------------------------
      if(try_item != []):  
#-------------------------------------------------------------------------------
        lever_check = 0  
        if(order_condition[item_no] in (1, 2)) and (value_s_list[item_no][2] < float(max_lever)):
          lever_check = 1  
          str_lever = str(value_s_list[item_no][2])
          apply_lever = str(int(Decimal(str_lever) / Decimal(lever_step)) * Decimal(lever_step))
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
        if(accum_num == 0): add_invest_usdt = invest_usdt
        else: add_invest_usdt = invest_usdt ** (accum_num + 1)
        if(accum_num == 5): add_invest_usdt = invest_usdt
#-------------------------------------------------------------------------------
        l_ex_price = str(h_price - float(tick_size))
        l_order_price = str(int(Decimal(l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_ex_qty = str((add_invest_usdt * float(l_sym_lever)) / float(l_order_price))
        l_order_qty = str(int(Decimal(l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        l_tp_ex_price = str(h_price + (limit_diff_p[item_no] * 1.3) + float(tick_size))
        l_tp_price = str(int(Decimal(l_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_st_ex_price = str(h_price - limit_diff_p[item_no] - float(tick_size))
        l_st_price = str(int(Decimal(l_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_order_side = 'Buy'
        l_order_position = 1
        l_ex_value = float(l_order_qty) * float(l_order_price) * 1.0
        l_ex_st_per = (abs(float(l_order_price) - float(l_st_price)) * float(l_sym_lever)) / float(l_order_price)

        s_ex_price = str(l_price + float(tick_size))
        s_order_price = str(int(Decimal(s_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_ex_qty = str((add_invest_usdt * float(s_sym_lever)) / float(s_order_price))
        s_order_qty = str(int(Decimal(s_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        s_tp_ex_price = str(l_price - (limit_diff_p[item_no] * 1.3) - float(tick_size))
        if(float(s_tp_ex_price) < (l_price * 0.15)): s_tp_ex_price = str(l_price * 0.15)
        s_tp_price = str(int(Decimal(s_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_st_ex_price = str(l_price + limit_diff_p[item_no] + float(tick_size))
        s_st_price = str(int(Decimal(s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        s_order_side = 'Sell'
        s_order_position = 2
        s_ex_value = float(s_order_qty) * float(s_order_price) * 1.0
        s_ex_st_per = (abs(float(s_order_price) - float(s_st_price)) * float(s_sym_lever)) / float(s_order_price)
#-------------------------------------------------------------------------------
        if(order_condition[item_no] not in (0, 9)):
#        if(order_condition[item_no] in (100, 900)):
#-------------------------------------------------------------------------------
          if(order_condition[item_no] == 1) and (lever_check == 1):
            if(long_qty == 0) and ((add_invest_usdt * 2) < avail_usdt) and (avail_order_num >= num):
                if(float(max_lever) >= float(l_sym_lever)):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0) and (s_ex_st_per < 0.6):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0) and (l_ex_st_per < 0.6):
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_tp_price, l_st_price]
                    order_market_part(add_order)
                    time.sleep(1)
          if(order_condition[item_no] == 2) and (lever_check == 1):
            if(short_qty == 0) and ((add_invest_usdt * 2) < avail_usdt) and (avail_order_num >= num):
                if(float(max_lever) >= float(s_sym_lever)):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0) and (l_ex_st_per < 0.6):
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, 1, l_tp_price, l_st_price]
                    conditional_market_part(add_order)
                    time.sleep(1)
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0) and (s_ex_st_per < 0.6):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_tp_price, s_st_price]                  
                    order_market_part(add_order)
                    time.sleep(1)
                  
          if(long_qty != 0) and ((add_invest_usdt * 1) < avail_usdt):
            if(order_condition[item_no] == 12) and ("Stop" not in stop_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
            if(order_condition[item_no] == 30) and ("Limit" not in limit_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    if(float(l_st_loss) != 0):
                      add_order = [sym_bol, '0', 1]
                      set_stop_loss_item(add_order)
                      time.sleep(1)
                    add_order = [sym_bol, 'Buy', l_order_qty, l_order_price, 1, l_tp_price, l_st_price]
                    order_limit_part(add_order)
                    time.sleep(1)

          if(short_qty != 0) and ((add_invest_usdt * 1) < avail_usdt):
            if(order_condition[item_no] == 21) and ("Stop" not in stop_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, 1, l_tp_price, l_st_price]
                    conditional_market_part(add_order)
                    time.sleep(1)
            if(order_condition[item_no] == 40) and ("Limit" not in limit_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    if(float(s_st_loss) != 0):  
                      add_order = [sym_bol, '0', 2]
                      set_stop_loss_item(add_order)
                      time.sleep(1)
                    add_order = [sym_bol, 'Sell', s_order_qty, s_order_price, 2, s_tp_price, s_st_price]                  
                    order_limit_part(add_order)
                    time.sleep(1)

          if(long_qty == 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[2] == 2):
            if(order_condition[item_no] == 41) and ("Stop" in stop_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_tp_price, l_st_price]
                    order_market_part(add_order)
                    time.sleep(1)
          if(short_qty == 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[1] == 1):
            if(order_condition[item_no] == 32) and ("Stop" in stop_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_tp_price, s_st_price]                  
                    order_market_part(add_order)
                    time.sleep(1)

          if(short_qty != 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[1] == 1):
            if(m_order_qty[1] > float(l_order_qty)) and ("Stop" in stop_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
                    time.sleep(1)
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, 1, l_tp_price, l_st_price]
                    conditional_market_part(add_order)
                    time.sleep(1)
          if(long_qty != 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[2] == 2):
            if(m_order_qty[2] > float(s_order_qty)) and ("Stop" in stop_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
                    time.sleep(1)
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(long_qty != 0) and (accum_pnl >= 0):
          ex_act_price = str(float(l_ent_price) + (abs(float(l_ent_price) - float(l_st_loss)) * 1.0))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(l_trailing) == 0) and (float(act_price) > sym_price):
            ex_ts_diff = abs(float(l_ent_price) - float(l_st_loss)) * 0.9
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 1]
            set_trading_stop_item(add_order)
#-------------------------------------------------------------------------------
#          if(accum_pnl < 0) and (abs(accum_pnl * 1.3) < float(l_unpnl)):
#            ex_ts_diff = abs(float(l_ent_price) - sym_price) * 0.3
#            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
#            add_order = [sym_bol, ts_diff, 1]
#            set_trading_stop_profit(add_order)
#-------------------------------------------------------------------------------
        if(short_qty != 0) and (accum_pnl >= 0):
          ex_act_price = str(float(s_ent_price) - (abs(float(s_ent_price) - float(s_st_loss)) * 1.0))
          act_price = str(int(Decimal(ex_act_price) / Decimal(tick_size)) * Decimal(tick_size))
          if(float(s_trailing) == 0) and (float(act_price) < sym_price):
            ex_ts_diff = abs(float(s_ent_price) - float(s_st_loss)) * 0.9
            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, ts_diff, act_price, 2]
            set_trading_stop_item(add_order)
#-------------------------------------------------------------------------------
#          if(accum_pnl < 0) and (abs(accum_pnl * 1.3) < float(s_unpnl)):
#            ex_ts_diff = abs(float(s_ent_price) - sym_price) * 0.3
#            ts_diff = str(int(Decimal(ex_ts_diff) / Decimal(tick_size)) * Decimal(tick_size))
#            add_order = [sym_bol, ts_diff, act_price, 2]
#            set_trading_stop_profit(add_order)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(long_qty != 0):
          if(created_time != 0) and (apply_time < limit_time):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
          if(created_time != 0) and (apply_time < final_time) and (float(l_unpnl) > (invest_usdt * 0.1)):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
          if(accum_pnl < 0) and (abs(accum_pnl * 1.3) < float(l_unpnl)):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
          
        if(short_qty != 0):
          if(created_time != 0) and (apply_time < limit_time):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
          if(created_time != 0) and (apply_time < final_time) and (float(s_unpnl) > (invest_usdt * 0.1)):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
          if(accum_pnl < 0) and (abs(accum_pnl * 1.3) < float(s_unpnl)):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
###############################################################################
        current_apply_time = datetime.fromtimestamp(int(apply_time / 1000)) + timedelta(hours=9)
        if(created_time != 0): trade_time = datetime.fromtimestamp(int(created_time / 1000)) + timedelta(hours=9)
        else: trade_time = 0
        if(long_qty != 0) and (short_qty != 0):
          print(sym_bol,sym_price,'accum_num:', accum_num, 'order_condition:',order_condition[item_no],'l_unpnl:',l_unpnl,'s_unpnl:',s_unpnl)
        elif(long_qty == 0) and (short_qty != 0):
          print(sym_bol,sym_price,'accum_num:', accum_num, 'order_condition:',order_condition[item_no],'s_unpnl:',s_unpnl,'s_liq_price:',s_liq_price,'invest_usdt:',add_invest_usdt)
        elif(long_qty != 0) and (short_qty == 0):
          print(sym_bol,sym_price,'accum_num:', accum_num, 'order_condition:',order_condition[item_no],'l_unpnl:',l_unpnl,'l_liq_price:',l_liq_price,'invest_usdt:',add_invest_usdt)
        else:
          print(sym_bol,sym_price,'order_condition:',order_condition[item_no], 'PASS')
        print('value_s:',value_s_list[item_no])
        print('value_v:',value_v_list[item_no])
        print('last_pnl:', last_pnl, 'accum_pnl:', accum_pnl, 'trade_time:',trade_time,'apply_time:',current_apply_time)
###############################################################################
###############################################################################
  korea_tz = pytz.timezone('Asia/Seoul')
  current_time_korea = datetime.now(korea_tz)
  current_time = current_time_korea.strftime('%Y-%m-%d %H:%M:%S')
  current_reset_time = datetime.fromtimestamp(reset_time/1000)
  current_limit_time = datetime.fromtimestamp(limit_time/1000)
  print('Live_USDT: ', round(live_usdt,2), 'My_USDT: ', round(my_usdt,2))
  print("Secure_usdt:", secure_usdt, "Avail_usdt:", round(avail_usdt,2),'invest_USDT:',round(invest_usdt,1))
  print("Avail_num:", avail_order_num, "L_num:", l_order_num, "S_num:", s_order_num, "Try_num:", len(try_item))
  print('current_time:',current_time,'reset_time:',current_reset_time,'limit_time:',current_limit_time,'Reset')
