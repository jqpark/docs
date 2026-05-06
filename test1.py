#v5_test15-3-6_SMA020_260213-1730
#v5 api
from binance.client import Client
from binance.exceptions import BinanceAPIException
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
###############################################################################
##############################################################################
def order_market_part(add_order):
    try:
        # add_order[3] (positionIdx) 값 처리: 
        # Bybit: 1(Buy side), 2(Sell side) 
        # Binance: 'LONG', 'SHORT' (Hedge Mode 기준)
        pos_side = "LONG" if add_order[3] == 1 else "SHORT"
        
        # 주문 실행
        order = client.futures_create_order(
            symbol=add_order[0],        # 코인 심볼 (예: 'BTCUSDT')
            side=add_order[1].upper(),  # 'BUY' 또는 'SELL' (대문자 필수)
            positionSide=pos_side,      # Hedge Mode일 경우 필수 ('LONG'/'SHORT')
            type='MARKET',              # 시장가 주문
            quantity=add_order[2],      # 수량
            # Binance는 기본 주문 시 TP/SL을 한 번에 넣기보다 
            # 별도의 조건부 주문(STOP_MARKET 등)을 거는 것이 일반적이지만,
            # 아래는 단순 시장가 주문 실행 로직입니다.
        )
        print(order)
        # TP/SL이 설정되어 있는 경우 별도의 주문으로 처리 (Binance 방식)
        if float(add_order[4]) > 0: # Take Profit
            client.futures_create_order(
                symbol=add_order[0],
                side='SELL' if add_order[1].upper() == 'BUY' else 'BUY',
                positionSide=pos_side,
                type='TAKE_PROFIT_MARKET',
                stopPrice=add_order[4],
                closePosition=True
            )
        if float(add_order[5]) > 0: # Stop Loss
            client.futures_create_order(
                symbol=add_order[0],
                side='SELL' if add_order[1].upper() == 'BUY' else 'BUY',
                positionSide=pos_side,
                type='STOP_MARKET',
                stopPrice=add_order[5],
                closePosition=True
            )
    except Exception as e:
        print(f"Error occurred: {e}")
    time.sleep(1)
##############################################################################
def order_limit_part(add_order):
    try:
        # add_order[4] (positionIdx) 값 처리: 1 -> 'LONG', 2 -> 'SHORT'
        pos_side = "LONG" if add_order[4] == 1 else "SHORT"
        
        # 1. 지정가 주문 실행
        order = client.futures_create_order(
            symbol=add_order[0],        # 코인 심볼
            side=add_order[1].upper(),  # 'BUY' 또는 'SELL'
            positionSide=pos_side,      # 'LONG' 또는 'SHORT'
            type='LIMIT',               # 지정가 주문
            timeInForce='GTC',          # Good Till Cancel
            quantity=add_order[2],      # 수량
            price=add_order[3]          # 진입 가격
        )
        print(order)
        # 2. 익절(Take Profit) 설정 (값이 있는 경우)
        if float(add_order[5]) > 0:
            client.futures_create_order(
                symbol=add_order[0],
                side='SELL' if add_order[1].upper() == 'BUY' else 'BUY',
                positionSide=pos_side,
                type='TAKE_PROFIT_MARKET',
                stopPrice=add_order[5], # 익절 가격
                closePosition=True,     # 포지션 전체 종료
                timeInForce='GTC'
            )
        # 3. 손절(Stop Loss) 설정 (값이 있는 경우)
        if float(add_order[6]) > 0:
            client.futures_create_order(
                symbol=add_order[0],
                side='SELL' if add_order[1].upper() == 'BUY' else 'BUY',
                positionSide=pos_side,
                type='STOP_MARKET',
                stopPrice=add_order[6], # 손절 가격
                closePosition=True,     # 포지션 전체 종료
                timeInForce='GTC'
            )
    except Exception as e:
        print(f"Error in order_limit_part: {e}")
    time.sleep(1)
##############################################################################
def conditional_market_part(add_order):
    try:
        # add_order[5] (positionIdx) 처리: 1 -> 'LONG', 2 -> 'SHORT'
        pos_side = "LONG" if add_order[5] == 1 else "SHORT"
        
        # 1. 조건부 시장가 진입 주문 (Stop Market)
        # Bybit의 triggerPrice -> Binance의 stopPrice
        order = client.futures_create_order(
            symbol=add_order[0],
            side=add_order[1].upper(),
            positionSide=pos_side,
            type='STOP_MARKET',      # 또는 'TAKE_PROFIT_MARKET'
            stopPrice=add_order[4],  # 발동 가격
            quantity=add_order[2],   # 주문 수량
            # workingType='MARK_PRICE' # 필요시 Mark Price(시장평균가) 기준으로 설정 가능
        )
        print(order)
        # 2. 익절(Take Profit) 설정 (값이 있는 경우)
        if float(add_order[6]) > 0:
            client.futures_create_order(
                symbol=add_order[0],
                side='SELL' if add_order[1].upper() == 'BUY' else 'BUY',
                positionSide=pos_side,
                type='TAKE_PROFIT_MARKET',
                stopPrice=add_order[6],
                closePosition=True
            )
        # 3. 손절(Stop Loss) 설정 (값이 있는 경우)
        if float(add_order[7]) > 0:
            client.futures_create_order(
                symbol=add_order[0],
                side='SELL' if add_order[1].upper() == 'BUY' else 'BUY',
                positionSide=pos_side,
                type='STOP_MARKET',
                stopPrice=add_order[7],
                closePosition=True
            )
    except Exception as e:
        print(f"Error in conditional_market_part: {e}")
    time.sleep(1)
##############################################################################
def closed_order_part(add_order):
    try:
        # 1. 현재 포지션 정보 가져오기
        symbol = add_order[0]
        pos_info = client.futures_position_information(symbol=symbol)
        
        # 데이터를 판다스 데이터프레임으로 변환 (Bybit 로직 유지)
        df = pd.DataFrame(pos_info)
        
        # Binance 결과에서 각 방향의 수량(positionAmt) 추출
        # positionAmt는 문자열이며, 숏 포지션의 경우 음수(-)로 올 수 있어 abs() 처리가 안전합니다.
        long_qty = abs(float(df[df['positionSide'] == 'LONG']['positionAmt'].values[0]))
        short_qty = abs(float(df[df['positionSide'] == 'SHORT']['positionAmt'].values[0]))
        
        # 2. 청산 수량 및 방향 결정
        # add_order[2]가 1이면 LONG 청산, 2이면 SHORT 청산으로 가정
        if add_order[2] == 1:
            closed_qty = long_qty
            pos_side = "LONG"
        elif add_order[2] == 2:
            closed_qty = short_qty
            pos_side = "SHORT"
        
        # 수량이 0보다 클 때만 청산 실행
        if closed_qty > 0:
            print(f"Closing {pos_side} position: {closed_qty}")
            # 3. 청산 주문 실행
            # Bybit의 side가 'Sell'이면 Binance도 'SELL' (단, positionSide와 조합 필요)
            # 보통 LONG 청산은 SELL, SHORT 청산은 BUY입니다.
            order = client.futures_create_order(
                symbol=symbol,
                side=add_order[1].upper(),  # 'BUY' 또는 'SELL'
                positionSide=pos_side,      # 'LONG' 또는 'SHORT'
                type='MARKET',
                quantity=closed_qty,
                reduceOnly=True             # 청산 전용 주문 설정
            )
            print(order)
        else:
            print(f"No active {pos_side} position to close.")
    except Exception as e:
        print(f"Error in closed_order_part: {e}")
    time.sleep(1)
##############################################################################
##############################################################################
def set_stop_loss_item(add_order):
    try:
        # add_order[2] (positionIdx) 처리: 1 -> 'LONG', 2 -> 'SHORT'
        pos_side = "LONG" if add_order[2] == 1 else "SHORT"
        
        # 포지션을 종료해야 하므로 사이드는 진입 방향과 반대여야 함
        # LONG 포지션의 손절은 SELL, SHORT 포지션의 손절은 BUY
        side = "SELL" if pos_side == "LONG" else "BUY"
        print(f"Setting Stop Loss for {add_order[0]} ({pos_side}) at {add_order[1]}")

        # 기존에 걸려있는 SL 주문이 있다면 충돌할 수 있으므로, 
        # 안전하게 기존 STOP_MARKET 주문들을 취소하고 새로 거는 로직이 권장되지만
        # 여기서는 Bybit 함수와 1:1 대응하도록 생성 로직만 작성합니다.
        
        res_ponse = client.futures_create_order(
            symbol=add_order[0],
            side=side,
            positionSide=pos_side,
            type='STOP_MARKET',
            stopPrice=add_order[1], # 손절 가격
            closePosition=True,      # 해당 포지션 전체 종료 (Bybit의 Full 모드와 유사)
            timeInForce='GTC'
        )
        print(res_ponse)
    except Exception as e:
        print(f"Error in set_stop_loss_item: {e}")
    time.sleep(1)
##############################################################################
##############################################################################
def set_trading_stop_item(add_order):
    try:
        # add_order[3] (positionIdx) 처리: 1 -> 'LONG', 2 -> 'SHORT'
        pos_side = "LONG" if add_order[3] == 1 else "SHORT"
        
        # 포지션 종료를 위한 사이드 설정
        # LONG 포지션의 트레일링 스톱은 SELL, SHORT 포지션은 BUY
        side = "SELL" if pos_side == "LONG" else "BUY"
        print(f"Setting Trailing Stop for {add_order[0]} ({pos_side})")

        # Binance의 trailing_stop_market 설정
        # activationPrice (활성화 가격): Bybit의 activePrice와 동일
        # callbackRate (콜백 비율): Bybit는 가격 차이(금액)를 넣기도 하지만, 
        # Binance는 퍼센트(예: 1.0은 1%)를 사용합니다.
        
        res_ponse = client.futures_create_order(
            symbol=add_order[0],
            side=side,
            positionSide=pos_side,
            type='TRAILING_STOP_MARKET',
            quantity=add_order[4],      # 수량 (추가 필요: Bybit와 달리 수량 명시 필수)
            activationPrice=add_order[2], # 특정 가격 도달 시 트레일링 시작
            callbackRate=add_order[1],    # 콜백 비율 (예: 0.1 ~ 5)
            reduceOnly=True
        )
        print(res_ponse)
    except Exception as e:
        print(f"Error in set_trading_stop_item: {e}")
    time.sleep(1)
################################################################################
################################################################################
def search_calc(sym_bol):
# Bybit 스타일의 itv_list
  itv_list = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w', '1M']
  for itv in itv_list:
#-------------------------------------------------------------------------------
# 1. 데이터 가져오기
    get_kline = client.futures_klines(symbol=sym_bol, interval=str(itv), limit=1000)
    time.sleep(1)

# 2. DataFrame 변환 및 리스트 파싱
    kline = pd.DataFrame(get_kline)
    if not kline.empty:  # 데이터가 있을 때만 실행
        t_list = kline[0].astype(int).tolist()
        o_list = kline[1].astype(float).tolist()
        h_list = kline[2].astype(float).tolist()
        l_list = kline[3].astype(float).tolist()
        c_list = kline[4].astype(float).tolist()
        v_list = kline[5].astype(float).tolist()
        p_list = kline[7].astype(float).tolist()
        t_list.reverse()
        o_list.reverse()
        h_list.reverse()
        l_list.reverse()
        c_list.reverse()
        v_list.reverse()
        p_list.reverse()
    else:
        print(f"Warning: No data for {sym_bol} on {itv}")
    continue # 데이터가 없으면 다음 인터벌로 넘어감
#-------------------------------------------------------------------------------
    cal_lever, order_position = 0, 0
    fr_vol, bk_vol, std_vol = 0, 0, 0
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
        if(bk_max < fr_max) and (bk_min > fr_min):
          order_position = 10
          cal_diff = abs(fr_max - fr_min)
          if(cal_diff == 0): cal_lever = 100

        l_selection, s_selection = 0, 0
        if(cal_lever <= 10) and (cal_lever >= 5): c_selection = 1
        if(order_position == 10) and (c_selection == 1): order_position = 1
        print(itv, sym_bol, order_position, cal_lever)
        break
      else: continue            
    if(min(fr_vol, bk_vol) > std_vol): break
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
  open_order_condition = 0
  limit_diff = order_value[3]
  s_value_list = order_value[4]
  v_value_list = order_value[5]
#-------------------------------------------------------------------------------
# 1. 숫자(분)와 바이낸스 간격 문자열 매칭 딕셔너리
  itv_map = {
    1: '1m', 3: '3m', 5: '5m', 15: '15m', 30: '30m',
    60: '1h', 120: '2h', 240: '4h', 360: '6h', 720: '12h'
  }
  itv_list = [3, 5, 15, 30, 60, 120, 240, 360, 720]
  for itv in itv_list:
    # 딕셔너리에서 숫자에 맞는 문자열을 가져옴 (없으면 기본값 '1d')
    binance_itv = itv_map.get(itv, '1d')
    
    # --- 시간 체크 로직 (ms 단위 교정) ---
    now_time_ms = int(time.time() * 1000)
    itv_ms = itv * 60 * 1000
    cal_time = now_time_ms - itv_ms
    if cal_time > apply_time: continue
    # ----------------------------------
    # 1. 데이터 가져오기 (매칭된 binance_itv 사용)
    get_kline = client.futures_klines(symbol=sym_bol, interval=binance_itv, limit=1000)
    time.sleep(1)
    # 2. DataFrame 변환 및 리스트 파싱 (이전과 동일)
    kline = pd.DataFrame(get_kline)
    if not kline.empty:
        t_list = kline[0].astype(int).tolist()
        o_list = kline[1].astype(float).tolist()
        h_list = kline[2].astype(float).tolist()
        l_list = kline[3].astype(float).tolist()
        c_list = kline[4].astype(float).tolist()
        v_list = kline[5].astype(float).tolist()
        p_list = kline[7].astype(float).tolist()
        
        # Bybit 순서대로 뒤집기 (0번이 최신)
        t_list.reverse(); o_list.reverse(); h_list.reverse(); 
        l_list.reverse(); c_list.reverse(); v_list.reverse(); p_list.reverse()
#-------------------------------------------------------------------------------
    cal_lever, order_position = 0, 0
    fr_vol, bk_vol, std_vol = 0, 0, 0
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
        if(bk_max < fr_max) and (bk_min > fr_min):
          order_position = 10
          cal_diff = abs(fr_max - fr_min)
          if(cal_diff == 0): cal_lever = 100

        l_selection, s_selection = 0, 0
        if(cal_lever <= 10) and (cal_lever >= 5): c_selection = 1
        if(order_position == 10) and (c_selection == 1): order_position = 1
      
        mx_time = float(t_list[bk_xnum] * 0.001)
        mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
        mn_time = float(t_list[bk_nnum] * 0.001)
        mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
        s_value_list = [order_position, fr_max, fr_min, bk_max, bk_min]
        v_value_list = [mx_server_time, mn_server_time, cal_lever]
        open_order_condition = 9
        limit_diff = cal_diff
        break
      else: continue            
    if(min(fr_vol, bk_vol) > std_vol): break
#-------------------------------------------------------------------------------
  time.sleep(1)
  order_return = [open_order_condition, limit_diff, s_value_list, v_value_list]
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
start_time = int(time.time())
while True:
  reset_time = int((int(time.time()) - (7 * 24 * 60 * 60)) * 1000)
  limit_time = int((int(time.time()) - (6 * 24 * 60 * 60)) * 1000)
  final_time = int((int(time.time()) - (5 * 24 * 60 * 60)) * 1000)
#-------------------------------------------------------------------------------
# 1. Binance 선물 계정 정보 가져오기
  account_info = client.futures_account()
  time.sleep(1)
# 2. 자산 리스트에서 USDT 정보만 추출
# assets 내의 여러 코인 중 USDT 데이터를 찾습니다.
  usdt_info = next(item for item in account_info['assets'] if item['asset'] == 'USDT')
# 3. 데이터 매칭 (Bybit 필드 -> Binance 필드)
# walletBalance: 미실현 손익 제외 순수 잔고
  my_usdt = float(usdt_info['walletBalance'])
# marginBalance: 지갑 잔고 + 미실현 손익 (Bybit의 equity와 동일)
  live_usdt = float(usdt_info['marginBalance'])
# positionInitialMargin: 현재 포지션을 유지하는 데 사용 중인 증거금
  tot_position = float(usdt_info['positionInitialMargin'])
# openOrderInitialMargin: 현재 미체결 주문에 걸려 있는 증거금
  total_order_im = float(usdt_info['openOrderInitialMargin'])
# 4. 사용 가능 잔고 (Available Balance)
# Binance는 가용 잔고를 직접 제공하므로 수동 계산보다 이 값을 사용하는 것이 더 정확합니다.
  avail_usdt = float(usdt_info['availableBalance'])
#-------------------------------------------------------------------------------
  max_l_usdt, min_l_usdt, origin_usdt = live_usdt, live_usdt, my_usdt
  max_m_usdt, min_m_usdt = my_usdt, my_usdt
  max_t_position = tot_position

  try_item = []
# 1. 전체 포지션 정보 가져오기
  pos_info = client.futures_position_information()
  get_positions = pd.DataFrame(pos_info)
  time.sleep(1)
  if get_positions.empty:
    long_list, short_list = [], []
  else:
    # 2. 수량이 0이 아닌(실제로 보유 중인) 포지션만 필터링
    # Binance는 모든 코인 리스트를 다 보내주므로 positionAmt가 0이 아닌 것을 골라야 합니다.
    active_positions = get_positions[get_positions['positionAmt'].astype(float) != 0]
    # 3. 롱 리스트 추출 (positionSide가 LONG인 경우)
    long_list = active_positions[active_positions['positionSide'] == 'LONG']
    long_list = long_list['symbol'].unique().tolist()
    # 4. 숏 리스트 추출 (positionSide가 SHORT인 경우)
    short_list = active_positions[active_positions['positionSide'] == 'SHORT']
    short_list = short_list['symbol'].unique().tolist()
    union_list = active_positions['symbol'].unique().tolist()
  try_list = union_list.copy()
#------------------------------------------------------------------------------- 
# 1. 모든 미체결 조건부 주문 가져오기 (Binance는 한 번에 최대 1000개까지 가능)
# 특정 symbol을 지정하지 않으면 전체 계정의 미체결 주문을 가져옵니다.
  res = client.futures_get_open_orders()
  open_orders = pd.DataFrame(res)
  time.sleep(1)
  if open_orders.empty: 
    check_order_list = []
  else: 
    # STOP_MARKET, TRAILING_STOP_MARKET 등 조건부 주문만 필터링하고 싶을 경우
    # stop_types = ['STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET']
    # check_order_list = open_orders[open_orders['type'].isin(stop_types)]['symbol'].unique().tolist()
    # 전체 미체결 주문 심볼 리스트
    check_order_list = open_orders['symbol'].unique().tolist()
print('check_order_list:', len(check_order_list))

# 2. 수익 확인 및 주문 취소 로직
  for sym_bol in check_order_list:
    if sym_bol not in try_list:
        # 최근 종료된 거래 내역 1개 가져오기 (Bybit의 get_closed_pnl 역할)
        # realizedPnl을 확인하기 위해 최신 거래 기록을 조회합니다.
        trades = client.futures_account_trades(symbol=sym_bol, limit=1)
        if not trades:
            last_pnl = 0
        else:
            # 최근 거래의 실현 손익 확인
            last_pnl = float(trades[0]['realizedPnl'])
        time.sleep(1)
        try_list.append(sym_bol)
        # 수익(PNL > 0)으로 종료되었다면 해당 심볼의 모든 미체결 주문 취소
        if last_pnl > 0:
            client.futures_cancel_all_open_orders(symbol=sym_bol)
            print(f"{sym_bol} 수익 종료 확인: 모든 주문 취소 완료")
# 3. try_list 업데이트 (기존 로직 유지)
  for sym_bol in try_list:
    if sym_bol not in check_order_list:
        check_order_list.append(sym_bol)
#-------------------------------------------------------------------------------
  l_order_num = len(long_list)
  s_order_num = len(short_list)
  secure_usdt = max(l_order_num, s_order_num) * invest_usdt * 0.5
  avail_order_num = int((avail_usdt - secure_usdt) / (invest_usdt * 2))
#-------------------------------------------------------------------------------
#  first_time = int(time.time())
#-------------------------------------------------------------------------------
# add item list
  ordered_item = 20
  #wish_item_no = 15
  wish_item_no = 100
  if(avail_order_num > 0) and (ordered_item > len(try_list)):
# 1. 모든 심볼의 24시간 티커 정보 가져오기
    tickers = client.futures_ticker_24hr()
    df = pd.DataFrame(tickers)
# 2. 데이터 타입 변환 및 필드 매칭
# quoteVolume: 24시간 거래대금 (Bybit의 turnover24h 역할)
# lastPrice: 현재가
# priceChangePercent: 24시간 가격 변동률 (%)
    df['quoteVolume'] = df['quoteVolume'].astype(float)
    df['lastPrice'] = df['lastPrice'].astype(float)
    df['priceChangePercent'] = df['priceChangePercent'].astype(float)
# 3. 변동률 절대값 기준 내림차순 정렬 (가장 많이 움직인 코인 순)
# Bybit의 'price24hPcnt'는 소수점 형태(0.05)일 수 있으나, Binance는 퍼센트(5.0) 형태입니다.
    sort_list = df.sort_values('priceChangePercent', key=lambda x: x.abs(), ascending=False, ignore_index=True)
# 4. 필터링 조건 적용
# - USDT 마켓만 필터링 (Binance는 모든 페어가 섞여 있음)
# - 가격이 투자금액의 2배 미만 (invest_usdt * 2)
# - 거래대금이 3,000만 USDT 이상 (3e7)
    added_list = sort_list[
        (sort_list['symbol'].str.endswith('USDT')) & 
        (sort_list['lastPrice'] < (invest_usdt * 2)) & 
        (sort_list['quoteVolume'] > 3e7)
    ]
# 5. 최종 심볼 리스트 추출
    added_symbols = added_list["symbol"].tolist()
#-------------------------------------------------------------------------------
    info = client.futures_exchange_info()
    # 상태가 'TRADING'아인 코인만 추출
    final_del_list = [s['symbol'] for s in info['symbols'] if s['status'] != 'TRADING' and s['quoteAsset'] == 'USDT']
   
    added_symbols = [x for x in added_symbols if x not in try_list]
    added_symbols = [x for x in added_symbols if x not in final_del_list]
    added_symbols = [x for x in added_symbols if 'USDT' in x]
    time.sleep(1)
    print('added_symbols:',len(added_symbols))
    if(added_symbols != []): try_list.extend(added_symbols)
    print('added_symbols:',len(added_symbols))
#-------------------------------------------------------------------------------
  try_item = try_list.copy()
  print('try_item:',len(try_item))
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
      apply_time = reset_time
###############################################################################
# 1. 특정 심볼의 티커 정보만 가져오기
# Bybit의 get_tickers(symbol=sym_bol)와 동일한 기능
      sym_info = client.futures_symbol_ticker(symbol=sym_bol)
# 2. 현재가 추출 (바이낸스는 'price'라는 키를 사용합니다)
      sym_price = float(sym_info['price'])

# 1. 특정 심볼의 포지션 정보 가져오기
      res_ponse = client.futures_position_information(symbol=sym_bol)
      df = pd.DataFrame(res_ponse)
# -------------------------------------------------------------------------------
      def clean(x):
        if x is None or str(x).strip() == "" or str(x) == "0":
            return 0
        return x
# -------------------------------------------------------------------------------
# 2. positionSide를 기준으로 인덱스 찾기 (Hedge Mode 기준)
# Binance는 보통 0: BOTH, 1: LONG, 2: SHORT 순서지만, 안전하게 필터링으로 인덱스를 잡습니다.
      try:
        l_idx = df[df['positionSide'] == 'LONG'].index[0]
        s_idx = df[df['positionSide'] == 'SHORT'].index[0]
      except IndexError:
    # 헤지 모드가 아니거나 데이터가 없을 경우를 대비한 예외 처리
        l_idx, s_idx = 0, 0 
# 3. 데이터 매칭 (Bybit 필드명 -> Binance 필드명)
# size -> positionAmt (단, Binance 숏 수량은 음수로 표기되므로 abs 처리)
      long_qty = abs(float(df['positionAmt'][l_idx]))
      short_qty = abs(float(df['positionAmt'][s_idx]))
# leverage -> leverage
      l_sym_lever = df['leverage'][l_idx]
      s_sym_lever = df['leverage'][s_idx]
# avgPrice -> entryPrice
      l_ent_price = float(df['entryPrice'][l_idx])
      s_ent_price = float(df['entryPrice'][s_idx])
# unrealisedPnl -> unrealizedProfit
      l_unpnl = float(df['unrealizedProfit'][l_idx])
      s_unpnl = float(df['unrealizedProfit'][s_idx])
# positionBalance / positionIM -> isolationWallet 또는 필드 없음
# Binance 선물에서는 격리 마진일 경우 'isolatedWallet'이 Bybit의 positionBalance와 유사합니다.
      l_position = float(df['isolatedWallet'][l_idx])
      s_position = float(df['isolatedWallet'][s_idx])

# tradeMode -> isIsolated (True/False로 반환됨)
      l_trade_mode = "Isolated" if df['isolated'][l_idx] else "Cross"
      s_trade_mode = "Isolated" if df['isolated'][s_idx] else "Cross"

# positionIM (증거금) -> positionInitialMargin (바이낸스 필드명)
      l_position_im = clean(df['positionInitialMargin'][l_idx])
      s_position_im = clean(df['positionInitialMargin'][s_idx])
# updatedTime -> updateTime (바이낸스는 ms 단위)
      l_created_time = clean(df['updateTime'][l_idx])
      s_created_time = clean(df['updateTime'][s_idx])
# liqPrice -> liquidationPrice
      l_liq_price = clean(df['liquidationPrice'][l_idx])
      s_liq_price = clean(df['liquidationPrice'][s_idx])

# 1. 해당 심볼의 모든 미체결 주문 가져오기
      open_orders_res = client.futures_get_open_orders(symbol=sym_bol)
      oo_df = pd.DataFrame(open_orders_res)
# 초기값 설정
      l_st_loss, s_st_loss = 0, 0
      l_trailing, s_trailing = 0, 0
      if not oo_df.empty:
    # --- [Stop Loss 추출] ---
    # 보통 STOP_MARKET 또는 STOP 타입을 사용합니다.
    # 롱 포지션의 손절은 'SELL' 주문이고, 숏 포지션의 손절은 'BUY' 주문입니다.
    # 롱 손절 (Side: SELL, Type: STOP_MARKET)
        l_sl_order = oo_df[(oo_df['side'] == 'SELL') & (oo_df['type'].str.contains('STOP'))]
        if not l_sl_order.empty:
        # stopPrice 필드에서 값을 가져옵니다.
            l_st_loss = float(l_sl_order['stopPrice'].iloc[0])
    # 숏 손절 (Side: BUY, Type: STOP_MARKET)
        s_sl_order = oo_df[(oo_df['side'] == 'BUY') & (oo_df['type'].str.contains('STOP'))]
        if not s_sl_order.empty:
            s_st_loss = float(s_sl_order['stopPrice'].iloc[0])
    # --- [Trailing Stop 추출] ---
    # Binance 타입 명칭: TRAILING_STOP_MARKET
    # 롱 트레일링 (Side: SELL)
        l_ts_order = oo_df[(oo_df['side'] == 'SELL') & (oo_df['type'] == 'TRAILING_STOP_MARKET')]
        if not l_ts_order.empty:
        # 트레일링은 보통 활성화 가격(activatePrice)을 기준으로 보거나 
        # 설정된 콜백 비율(callbackRate) 등을 확인합니다. 여기서는 활성화 가격을 넣어줍니다.
            l_trailing = float(l_ts_order['activatePrice'].iloc[0])
    # 숏 트레일링 (Side: BUY)
        s_ts_order = oo_df[(oo_df['side'] == 'BUY') & (oo_df['type'] == 'TRAILING_STOP_MARKET')]
        if not s_ts_order.empty:
            s_trailing = float(s_ts_order['activatePrice'].iloc[0])
        

# 1. 전체 거래소 정보 가져오기 (특정 심볼만 필터링)
      exchange_info = client.futures_exchange_info()
      info = next(s for s in exchange_info['symbols'] if s['symbol'] == sym_bol)
# 2. 필터 데이터 파싱
# Binance는 'filters'라는 리스트 안에 각 필터가 딕셔너리 형태로 들어있습니다.
      filters = {f['filterType']: f for f in info['filters']}
# 3. 값 추출 및 매칭
# LOT_SIZE 필터
      qty_step = filters['LOT_SIZE']['stepSize']
      min_qty = filters['LOT_SIZE']['minQty']
# MIN_NOTIONAL (최소 주문 금액)
      min_value = filters.get('MIN_NOTIONAL', {}).get('notional', '5') # 기본값 5 USDT
# PRICE_FILTER (가격 단위)
      tick_size = filters['PRICE_FILTER']['tickSize']
# 레버리지 및 기타 정보
      max_lever = info['leverage'] # Binance는 symbols 정보 안에 바로 들어있거나
      min_lever = 1               # 기본적으로 1배가 최소입니다.
      lever_step = 1              # Binance 선물 레버리지는 정수 단위(1)로 조절됩니다.
      status = info['status'] # 'TRADING' 등


# 1. Binance 선물 계정 정보 가져오기
      account_info = client.futures_account()
      time.sleep(1)
# 2. 자산 리스트에서 USDT 정보만 추출
# assets 내의 여러 코인 중 USDT 데이터를 찾습니다.
      usdt_info = next(item for item in account_info['assets'] if item['asset'] == 'USDT')
# 3. 데이터 매칭 (Bybit 필드 -> Binance 필드)
# walletBalance: 미실현 손익 제외 순수 잔고
      my_usdt = float(usdt_info['walletBalance'])
# marginBalance: 지갑 잔고 + 미실현 손익 (Bybit의 equity와 동일)
      live_usdt = float(usdt_info['marginBalance'])
# positionInitialMargin: 현재 포지션을 유지하는 데 사용 중인 증거금
      tot_position = float(usdt_info['positionInitialMargin'])
# openOrderInitialMargin: 현재 미체결 주문에 걸려 있는 증거금
      total_order_im = float(usdt_info['openOrderInitialMargin'])
# 4. 사용 가능 잔고 (Available Balance)
# Binance는 가용 잔고를 직접 제공하므로 수동 계산보다 이 값을 사용하는 것이 더 정확합니다.
      avail_usdt = float(usdt_info['availableBalance'])
#-------------------------------------------------------------------------------
# trade 조회
# 1. 특정 심볼의 최근 체결 내역 가져오기 (Trade 전용)
# limit=10으로 최근 10개를 가져와서 가장 최근 것을 분석합니다.
      try:
        res = client.futures_account_trades(symbol=sym_bol, limit=10)
        if not res:
        # 체결 내역이 없는 경우 초기값 설정
            created_time, exec_price, trade_side, trade_type = 0, 0, 0, "None"
        else:
        # 2. 데이터프레임 변환 및 정렬 (시간순 내림차순)
            last_trade_df = pd.DataFrame(res)
            last_trade_df = last_trade_df.sort_values("time", ascending=False)
        # 3. 최신 체결 데이터 추출
            latest = last_trade_df.iloc[0]
            created_time = int(latest["time"])     # 체결 시간 (ms)
            exec_price = float(latest["price"])    # 체결 가격
            trade_side = latest["side"]            # BUY 또는 SELL
        # 4. 주문 타입 추출 (Binance 체결 내역엔 이 정보가 직접 없으므로 주문 상세 조회 필요)
        # 만약 stopOrderType 정보가 반드시 필요하다면 orderId로 재조회합니다.
            try:
                order_info = client.futures_get_order(symbol=sym_bol, orderId=latest['orderId'])
                trade_type = order_info['origType'] # 예: STOP_MARKET, TRAILING_STOP_MARKET 등
            except:
                trade_type = "None"
      except Exception as e:
        print(f"execution API error: {e}")
        created_time, exec_price, trade_side, trade_type = 0, 0, 0, "None"
# time.sleep(1) # 필요 시 활성화
#-------------------------------------------------------------------------------
# closed pnl 조회
# 1. 특정 시간(reset_time) 이후의 거래 내역 가져오기
      try:
    # Binance는 startTime을 인자로 받을 수 있습니다 (단위: ms)
        res_pnl_data = client.futures_account_trades(symbol=sym_bol, startTime=reset_time)
        if not res_pnl_data:
            closed_pnl_df = pd.DataFrame()
        else:
            closed_pnl_df = pd.DataFrame(res_pnl_data)
        # 실현 손익(realizedPnl)이 0이 아닌 것만 필터링 (순수 거래 수수료 제외, 포지션 종료 관련)
            closed_pnl_df = closed_pnl_df[closed_pnl_df['realizedPnl'].astype(float) != 0]
        if closed_pnl_df.empty:
            last_pnl = 0
            closed_time, closed_side, pnl_list, avg_entry_price, avg_exit_price = [], [], [], [], []
        else:
        # 2. 최신순 정렬 (updatedTime 대신 time 필드 사용)
            closed_pnl_df = closed_pnl_df.sort_values("time", ascending=False)
        # 3. 값 추출 및 리스트화
        # Binance의 realizedPnl은 각 체결 건별 수익입니다.
            last_pnl = float(closed_pnl_df.iloc[0]["realizedPnl"])
            closed_time = closed_pnl_df["time"].astype(int).tolist()
        # Binance는 각 거래의 평균 진입가를 제공하지 않으므로, 
        # API에서 제공하는 realizedPnl과 price(체결가)를 사용합니다.
            avg_exit_price = closed_pnl_df["price"].astype(float).tolist()
        # Binance 'trades' API는 포지션의 avgEntryPrice를 직접 주지 않습니다.
        # 필요하다면 0으로 채우거나 별도 계산 로직이 필요합니다.
            avg_entry_price = [0] * len(closed_time) 
        
        # 포지션 종료 방향 (바이낸스는 주문 방향을 side로 표시)
            closed_side = closed_pnl_df["side"].tolist()
            pnl_list = closed_pnl_df["realizedPnl"].astype(float).tolist()
      except Exception as e:
        print(f"closed_pnl API error: {e}")
#-------------------------------------------------------------------------------
# order history 조회
      apply_time = created_time
      apply_price = exec_price
      entry_price, exit_price = 0, 0
      accum_num, accum_pnl = 0, 0
      filtered_pri, entry_p_list, exit_p_list = [], [], []
      # 1. 특정 시간(reset_time) 이후의 전체 주문 내역 가져오기
      try:
        res_order = client.futures_get_all_orders(symbol=sym_bol, startTime=reset_time)
        order_history = pd.DataFrame(res_order)
        if order_history.empty:
            open_time, open_side, open_client_id = [], [], []
        else:
        # 2. 필터링 로직 (Bybit 조건 이식)
        # - Market/Limit 주문이거나 STOP 관련 주문일 것
        # - reduceOnly가 False일 것 (신규 진입 주문)
        # - 상태가 Filled(체결) 또는 PartiallyFilled(부분체결)일 것
            order_open = order_history[
                (
                    (order_history['type'].isin(['LIMIT', 'MARKET'])) | 
                    (order_history['type'].str.contains('STOP'))
                ) & 
                (order_history['reduceOnly'] == False) & 
                (order_history['status'].isin(['FILLED', 'PARTIALLY_FILLED']))
            ]
        # 3. 정렬 및 데이터 추출 (업데이트 시간 기준 내림차순)
            order_open = order_open.sort_values("updateTime", ascending=False)
            open_time = order_open["updateTime"].astype(int).tolist()
            open_side = order_open["side"].tolist()
            open_client_id = order_open["clientOrderId"].tolist() # orderLinkId 역할
        # 4. 'First'가 포함된 주문 찾기 (주문 전략의 시작점 확인)
            order_index = next((i for i, x in enumerate(open_client_id) if 'First' in x), -1)
            if order_index == -1:
                apply_time = created_time
                apply_price = exec_price
                accum_num, accum_pnl = 0, 0
            else:
                apply_time = open_time[order_index]
                accum_num = order_index
            # 이전 단계에서 구한 closed_time, pnl_list 활용 (누적 수익 계산)
                filtered_pnl = [p for t, p in zip(closed_time, pnl_list) if t >= apply_time]
                accum_pnl = sum(filtered_pnl)
            # 진입/청산 가격 리스트 필터링
                entry_p_list = [p for t, p in zip(closed_time, avg_entry_price) if t >= apply_time]
                if not entry_p_list or entry_p_list[-1] == 0:
                # Binance는 trades API에서 avgEntryPrice를 안 주므로, 
                # 데이터가 없으면 현재 체결가(exec_price)를 대입
                    apply_price, entry_price = exec_price, 0
                else:
                    apply_price, entry_price = entry_p_list[-1], entry_p_list[-1]
                exit_p_list = [p for t, p in zip(closed_time, avg_exit_price) if t >= apply_time]
                exit_price = exit_p_list[-1] if exit_p_list else 0
      except Exception as e:
        print(f"order_history API error: {e}")
#-------------------------------------------------------------------------------
      if(entry_price == 0) and (exit_price == 0):
        if(long_qty != 0): entry_price, exit_price = float(l_ent_price), float(l_st_loss)
        if(short_qty != 0): entry_price, exit_price = float(s_ent_price), float(s_st_loss)
      diff_gap = Decimal(str(abs(entry_price - exit_price))) / Decimal(tick_size)
      diff_gap = float(int(diff_gap) * Decimal(tick_size))
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
      if(long_qty != 0) and (diff_gap == 0):
          add_order = [sym_bol, "Sell", 1]
          closed_order_part(add_order)
          time.sleep(1)
          print(sym_bol, "L_ERROR")
          session.cancel_all_orders(category="linear", symbol=sym_bol)
          continue
      if(short_qty != 0) and (diff_gap == 0):
          add_order = [sym_bol, "Buy", 2]
          closed_order_part(add_order)
          time.sleep(1)
          print(sym_bol, "S_ERROR")
          session.cancel_all_orders(category="linear", symbol=sym_bol)
          continue
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------        
      if(trail_item == 1):
        if("Limit" in limit_order_list):
          session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='Order')
        if("Stop" in stop_order_list):
          session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
        print(sym_bol, "trail_item")
        continue
#-------------------------------------------------------------------------------
      if(long_qty == 0) and (short_qty == 0):
          if("Stop" not in stop_order_list) and ("Limit" not in limit_order_list):
            search_calc_result = search_calc(sym_bol)
            order_condition[item_no] = search_calc_result[0]
            limit_diff_p[item_no] = search_calc_result[1]
            value_s_list[item_no] = search_calc_result[2]
            value_v_list[item_no] = search_calc_result[3]
            if(order_condition[item_no] in (1, 2)): num = num + 1
          
      if("Stop" not in stop_order_list) and (trail_item == 0) and (sym_bol in union_list):
        stop_condition = 0  
        if(accum_num == 0):
          if(long_qty != 0) and (short_qty == 0):
            order_calc_result = order_calc(sym_bol, apply_time, 1, float(l_ent_price), diff_gap, float(l_sym_lever), stop_condition)
          if(long_qty == 0) and (short_qty != 0):
            order_calc_result = order_calc(sym_bol, apply_time, 2, float(s_ent_price), diff_gap, float(s_sym_lever), stop_condition)
        if(accum_num != 0):
          if(long_qty != 0) and (short_qty == 0):
            order_calc_result = order_calc(sym_bol, apply_time, 3, float(l_ent_price), diff_gap, float(l_sym_lever), stop_condition)
          if(long_qty == 0) and (short_qty != 0):
            order_calc_result = order_calc(sym_bol, apply_time, 4, float(s_ent_price), diff_gap, float(s_sym_lever), stop_condition)
        order_condition[item_no] = order_calc_result[0]
        limit_diff_p[item_no] = order_calc_result[1]
        value_s_list[item_no] = order_calc_result[2]
        value_v_list[item_no] = order_calc_result[3]
            
      if("Stop" in stop_order_list) and ("Limit" not in limit_order_list) and (trail_item == 0):
        if(accum_num != 0):
          stop_condition = 1
          if(long_qty != 0) and (short_qty == 0):
            order_calc_result = order_calc(sym_bol, apply_time, 1, float(l_ent_price), diff_gap, float(l_sym_lever), stop_condition)
          if(long_qty == 0) and (short_qty != 0):
            order_calc_result = order_calc(sym_bol, apply_time, 2, float(s_ent_price), diff_gap, float(s_sym_lever), stop_condition)
          if(long_qty == 0) and (short_qty == 0) and (pnl_list != []) and (pnl_list[0] < 0):
            if(m_order_idx[1] == 1):
              order_calc_result = order_calc(sym_bol, apply_time, 3, m_order_tp[1], diff_gap, float(l_sym_lever), stop_condition)
            if(m_order_idx[2] == 2):
              order_calc_result = order_calc(sym_bol, apply_time, 4, m_order_tp[2], diff_gap, float(s_sym_lever), stop_condition)
        if(accum_num == 0):
          stop_condition = 2
          if(long_qty != 0) and (short_qty == 0):
            order_calc_result = order_calc(sym_bol, apply_time, 1, float(l_ent_price), diff_gap, float(l_sym_lever), stop_condition)
          if(long_qty == 0) and (short_qty != 0):
            order_calc_result = order_calc(sym_bol, apply_time, 2, float(s_ent_price), diff_gap, float(s_sym_lever), stop_condition)
          if(long_qty == 0) and (short_qty == 0) and (pnl_list != []) and (pnl_list[0] < 0):
            if(m_order_idx[1] == 1):
              order_calc_result = order_calc(sym_bol, apply_time, 3, m_order_tp[1], diff_gap, float(l_sym_lever), stop_condition)
            if(m_order_idx[2] == 2):
              order_calc_result = order_calc(sym_bol, apply_time, 4, m_order_tp[2], diff_gap, float(s_sym_lever), stop_condition)
        order_condition[item_no] = order_calc_result[0]
        limit_diff_p[item_no] = order_calc_result[1]
        value_s_list[item_no] = order_calc_result[2]
        value_v_list[item_no] = order_calc_result[3]
           
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
        retry_num, retry_condition = 5, 0
        max_ls_usdt = invest_usdt * (2 ** (retry_num))
        add_invest_usdt = invest_usdt * (2 ** (accum_num + 1))
        if((add_invest_usdt * 1) > avail_usdt):
          add_invest_usdt = invest_usdt
        if(long_qty == 0) and (short_qty == 0):
          if("Stop" not in stop_order_list) and ("Limit" not in limit_order_list):
            add_invest_usdt = invest_usdt
#        add_invest_usdt = invest_usdt
#-------------------------------------------------------------------------------
        l_ex_price = str(h_price - float(tick_size))
        l_order_price = str(int(Decimal(l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
        l_ex_qty = str((add_invest_usdt * float(l_sym_lever)) / float(l_order_price))
        l_order_qty = str(int(Decimal(l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
        l_tp_ex_price = str(h_price + (limit_diff_p[item_no] * 2.0) + float(tick_size))
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
        s_tp_ex_price = str(l_price - (limit_diff_p[item_no] * 2.0) - float(tick_size))
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
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0) and (l_ex_st_per < 0.6):
                    order_linkid = f"{sym_bol}_First_L_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_tp_price, l_st_price, order_linkid]
                    order_market_part(add_order)
                    time.sleep(1)
          if(order_condition[item_no] == 2) and (lever_check == 1):
            if(short_qty == 0) and ((add_invest_usdt * 2) < avail_usdt) and (avail_order_num >= num):
                if(float(max_lever) >= float(s_sym_lever)):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0) and (s_ex_st_per < 0.6):
                    order_linkid = f"{sym_bol}_First_S_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_tp_price, s_st_price, order_linkid]                  
                    order_market_part(add_order)
                    time.sleep(1)

          if(long_qty != 0) and ((add_invest_usdt * 1) < avail_usdt):
            if(order_condition[item_no] == 12) and ("Stop" not in stop_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    order_linkid = f"{sym_bol}_Condition_S_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price, order_linkid]                  
                    conditional_market_part(add_order)
                    time.sleep(1)
#            if(order_condition[item_no] == 13) and ("Limit" not in limit_order_list):
#                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
#                    if(float(l_st_loss) != 0):
#                      add_order = [sym_bol, '0', 1]
#                      set_stop_loss_item(add_order)
#                      time.sleep(1)
#                    order_linkid = f"{sym_bol}_Limit_S_{int(time.time()*1000)}"
#                    add_order = [sym_bol, 'Buy', l_order_qty, l_order_price, 1, l_tp_price, l_st_price, order_linkid]
#                    order_limit_part(add_order)
#                    time.sleep(1)

          if(short_qty != 0) and ((add_invest_usdt * 1) < avail_usdt):
            if(order_condition[item_no] == 21) and ("Stop" not in stop_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    order_linkid = f"{sym_bol}_Condition_L_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, 1, l_tp_price, l_st_price, order_linkid]
                    conditional_market_part(add_order)
                    time.sleep(1)
#            if(order_condition[item_no] == 24) and ("Limit" not in limit_order_list):
#                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
#                    if(float(s_st_loss) != 0):  
#                      add_order = [sym_bol, '0', 2]
#                      set_stop_loss_item(add_order)
#                      time.sleep(1)
#                    order_linkid = f"{sym_bol}_Limit_S_{int(time.time()*1000)}"
#                    add_order = [sym_bol, 'Sell', s_order_qty, s_order_price, 2, s_tp_price, s_st_price, order_linkid]                  
#                    order_limit_part(add_order)
#                    time.sleep(1)

          if(short_qty != 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[1] == 1):
            if((m_order_qty[1] * 1.5) < float(l_order_qty)):
                if(order_condition[item_no] == 23) and ("Limit" not in limit_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
                    time.sleep(1)
                    order_linkid = f"{sym_bol}_ReConditon_L_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_order_price, 1, l_tp_price, l_st_price, order_linkid]
                    conditional_market_part(add_order)
                    time.sleep(1)
          if(long_qty != 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[2] == 2):
            if((m_order_qty[2] * 1.5) < float(s_order_qty)):
                if(order_condition[item_no] == 14) and ("Limit" not in limit_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    session.cancel_all_orders(category="linear", symbol=sym_bol,orderFilter='StopOrder',stopOrderType='Stop')
                    time.sleep(1)
                    order_linkid = f"{sym_bol}_ReConditon_S_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_order_price, 2, s_tp_price, s_st_price, order_linkid]                  
                    conditional_market_part(add_order)
                    time.sleep(1)

          if(long_qty == 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[2] == 2):
            if(order_condition[item_no] == 41) and ("Stop" in stop_order_list):
                  if(float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                    order_linkid = f"{sym_bol}_Market_L_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Buy', l_order_qty, 1, l_tp_price, l_st_price, order_linkid]
                    order_market_part(add_order)
                    time.sleep(1)
          if(short_qty == 0) and ((add_invest_usdt * 1) < avail_usdt) and (m_order_idx[1] == 1):
            if(order_condition[item_no] == 32) and ("Stop" in stop_order_list):
                  if(float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                    order_linkid = f"{sym_bol}_Market_S_{int(time.time()*1000)}"
                    add_order = [sym_bol, 'Sell', s_order_qty, 2, s_tp_price, s_st_price, order_linkid]
                    order_market_part(add_order)
                    time.sleep(1)          
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
        if(long_qty != 0) and (accum_pnl >= 0):
#        if(long_qty != 0):
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
#        if(short_qty != 0):
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
          if(accum_pnl < 0) and (abs(accum_pnl * 2.0) < float(l_unpnl)):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
          if(max_ls_usdt <= abs(accum_pnl + float(l_unpnl))):
            add_order = [sym_bol, "Sell", 1]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
            print(sym_bol, "max_ls_usdt OVER")

          
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
          if(accum_pnl < 0) and (abs(accum_pnl * 2.0) < float(s_unpnl)):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
          if(max_ls_usdt <= abs(accum_pnl + float(s_unpnl))):
            add_order = [sym_bol, "Buy", 2]
            closed_order_part(add_order)
            time.sleep(1)
            session.cancel_all_orders(category="linear", symbol=sym_bol)
            time.sleep(1)
            print(sym_bol, "max_ls_usdt OVER")
###############################################################################
        current_apply_time = datetime.fromtimestamp(int(apply_time / 1000)) + timedelta(hours=9)
        if(created_time != 0): trade_time = datetime.fromtimestamp(int(created_time / 1000)) + timedelta(hours=9)
        else: trade_time = 0
        if(long_qty != 0) and (short_qty != 0):
          print(sym_bol,sym_price, 'order_condition:',order_condition[item_no],'l_unpnl:',l_unpnl,'s_unpnl:',s_unpnl)
        elif(long_qty == 0) and (short_qty != 0):
          print(sym_bol,sym_price, 'order_condition:',order_condition[item_no],'s_unpnl:',s_unpnl,'s_liq_price:',s_liq_price,'invest_usdt:',add_invest_usdt)
        elif(long_qty != 0) and (short_qty == 0):
          print(sym_bol,sym_price, 'order_condition:',order_condition[item_no],'l_unpnl:',l_unpnl,'l_liq_price:',l_liq_price,'invest_usdt:',add_invest_usdt)
        else:
          print(sym_bol,sym_price,'order_condition:',order_condition[item_no], 'PASS')
#        print('value_s:',value_s_list[item_no])
#        print('value_v:',value_v_list[item_no])
        print('accum_num:', accum_num, 'accum_pnl:', accum_pnl, 'apply_price:', apply_price, 'apply_time:', current_apply_time)
        print('last_pnl:', last_pnl, 'diff_gap:', diff_gap, 'trade_time:', trade_time)
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
