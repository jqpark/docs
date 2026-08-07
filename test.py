#Replit
from binance.client import Client
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
if origin_time >= reset_time:
    start_time = origin_time
else:
    start_time = reset_time
##############################################################################
##############################################################################
chat_id = os.getenv("chat_id")
order_id = os.getenv("order_id")
client = Client(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# positionIdx (1: LONG, 2: SHORT) -> 바이낸스 positionSide 변환 헬퍼
def get_position_side(pos_idx):
    if pos_idx == 1:
        return "LONG"
    elif pos_idx == 2:
        return "SHORT"
    return "BOTH"  # 단방향 모드일 경우
##############################################################################
# 1. 시장가 주문 (order_market_part)
##############################################################################
def order_market_part(add_order):
    # add_order: [symbol, side, qty, positionIdx, takeProfit, stopLoss, orderLinkId]
    symbol = add_order[0]
    side = add_order[1].upper()  # 'BUY' or 'SELL'
    qty = float(add_order[2])
    pos_side = get_position_side(add_order[3])
    tp = add_order[4]
    sl = add_order[5]
    client_id = add_order[6]
    # 1) 메인 시장가 주문
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'MARKET',
        'quantity': qty,
        'positionSide': pos_side,
        'newClientOrderId': client_id
    }
    res = client.futures_create_order(**params)
    print(res)
    # 2) Take Profit / Stop Loss 개별 조건부 주문 제출 (설정값이 있는 경우)
    opp_side = 'SELL' if side == 'BUY' else 'BUY'
    if sl and float(sl) > 0:
        client.futures_create_order(
            symbol=symbol,
            side=opp_side,
            type='STOP_MARKET',
            stopPrice=float(sl),
            closePosition=True,
            positionSide=pos_side
        )
    if tp and float(tp) > 0:
        client.futures_create_order(
            symbol=symbol,
            side=opp_side,
            type='TAKE_PROFIT_MARKET',
            stopPrice=float(tp),
            closePosition=True,
            positionSide=pos_side
        )
    time.sleep(1)
##############################################################################
# 2. 지정가 주문 (order_limit_part)
##############################################################################
def order_limit_part(add_order):
    # add_order: [symbol, side, qty, price, positionIdx, takeProfit, stopLoss, orderLinkId]
    symbol = add_order[0]
    side = add_order[1].upper()
    qty = float(add_order[2])
    price = float(add_order[3])
    pos_side = get_position_side(add_order[4])
    tp = add_order[5]
    sl = add_order[6]
    client_id = add_order[7]
    res = client.futures_create_order(
        symbol=symbol,
        side=side,
        type='LIMIT',
        timeInForce='GTC',
        quantity=qty,
        price=price,
        positionSide=pos_side,
        newClientOrderId=client_id
    )
    print(res)
    # TP / SL 설정
    opp_side = 'SELL' if side == 'BUY' else 'BUY'
    if sl and float(sl) > 0:
        client.futures_create_order(
            symbol=symbol, side=opp_side, type='STOP_MARKET',
            stopPrice=float(sl), closePosition=True, positionSide=pos_side
        )
    if tp and float(tp) > 0:
        client.futures_create_order(
            symbol=symbol, side=opp_side, type='TAKE_PROFIT_MARKET',
            stopPrice=float(tp), closePosition=True, positionSide=pos_side
        )
    time.sleep(1)
##############################################################################
# 3. 조건부 시장가 주문 (conditional_market_part)
##############################################################################
def conditional_market_part(add_order):
    # add_order: [symbol, side, qty, triggerDirection, triggerPrice, positionIdx, takeProfit, stopLoss, orderLinkId]
    symbol = add_order[0]
    side = add_order[1].upper()
    qty = float(add_order[2])
    trigger_price = float(add_order[4])
    pos_side = get_position_side(add_order[5])
    client_id = add_order[8]
    # 바이낸스에서는 STOP_MARKET 타입을 사용하며 triggerPrice 대신 stopPrice를 입력합니다.
    res = client.futures_create_order(
        symbol=symbol,
        side=side,
        type='STOP_MARKET',
        quantity=qty,
        stopPrice=trigger_price,
        positionSide=pos_side,
        newClientOrderId=client_id
    )
    print(res)
    time.sleep(1)
##############################################################################
# 4. 포지션 전량 시장가 청산 (closed_order_part)
##############################################################################
def closed_order_part(add_order):
    # add_order: [symbol, side, positionIdx]
    symbol = add_order[0]
    side = add_order[1].upper()
    pos_idx = add_order[2]
    pos_side = get_position_side(pos_idx)
    # 1) 현재 포지션 정보 조회
    positions = client.futures_position_information(symbol=symbol)
    # 헤지 모드에서 해당 positionSide의 수량 찾기
    closed_qty = 0.0
    for pos in positions:
        if pos['positionSide'] == pos_side:
            closed_qty = abs(float(pos['positionAmt']))
            break
    # 2) 포지션 수량이 있는 경우 전량 청산 주문 제출
    if closed_qty > 0:
        res = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=closed_qty,
            positionSide=pos_side,
            reduceOnly=True if pos_side == 'BOTH' else False  # Hedge Mode에서는 closePosition 또는 positionSide 지정으로 처리됨
        )
        print(res)
    time.sleep(1)
##############################################################################
# 5. 손절가 설정/수정 (set_stop_loss_item)
##############################################################################
def set_stop_loss_item(add_order):
    symbol, stop_price, pos_mode = add_order[0], add_order[1], add_order[2]
    # 1. 기존에 걸려있는 STOP_MARKET 주문 취소 (중복 실행 방지)
    open_orders = client.futures_get_open_orders(symbol=symbol)
    for order in open_orders:
        if order["type"] in ["STOP_MARKET", "STOP"]:
            client.futures_cancel_order(
                symbol=symbol, orderId=order["orderId"]
            )
    # 2. 포지션 방향 및 주문 방향 설정
    # pos_mode: 1 = Long, 2 = Short
    side = "SELL" if pos_mode == 1 else "BUY"
    pos_side = "LONG" if pos_mode == 1 else "SHORT"
    # 3. 바이낸스 Stop Loss 주문 실행 (closePosition=True로 설정하여 포지션 전량 청산)
    # 헤지 모드인 경우 positionSide 지정, 단방향 모드인 경우 생략 가능
    client.futures_create_order(
        symbol=symbol,
        side=side,
        type="STOP_MARKET",
        stopPrice=stop_price,
        closePosition=True,
        positionSide=pos_side,  # 헤지 모드 사용 시 필수
    )
    print(
        f"[{symbol}] 바이낸스 손절 주문 등록 완료 (가격: {stop_price}, 방향: {pos_side})"
    )
##############################################################################
##############################################################################
# 6. 주문 취소 (cancel_all_orders)
##############################################################################
def cancel_all_orders(sym_bol):
    client.futures_cancel_all_open_orders(symbol=sym_bol)
    print(f"[{sym_bol}] 모든 미체결 및 TP/SL 대기 주문 취소 완료")
##############################################################################
def search_calc(sym_bol, accum_num):
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
  l_next_price, s_next_price = cal_max, cal_min
  mx_time = float(t_list[xnum] * 0.001)
  mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
  mn_time = float(t_list[nnum] * 0.001)
  mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
  s_value_list = [l_next_price, s_next_price, round(cal_lever, 2)]
  v_value_list = [itv, mx_server_time, mn_server_time]
#-------------------------------------------------------------------------------
  order_return = [order_position, limit_diff, s_value_list, v_value_list]
  return(order_return)
###############################################################################    
###############################################################################
def order_calc(sym_bol, apply_time, order_side):
  order_position = 9
  itv_list = ['3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h']
  itv_num = [3, 5, 15, 30, 60, 120, 240, 360, 720]
  for itv in itv_list:
    itv_index = itv_list.index(itv)
    now_time = int(time.time())
    candle_range_ms = itv_num[itv_index] * 60 * 1000 * 1000
    cal_time = (now_time * 1000) - candle_range_ms
    if(cal_time > apply_time): continue
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
    for sta in range(len(t_list)):
        if(t_list[sta] < apply_time): break
#-------------------------------------------------------------------------------
    max_lever, min_lever, cal_lever, fr_per = 5, 10, 99, 0
    pre_condition = 0
#    sta = 100
    max_diff = c_list[sta] * 0.5 / max_lever
    min_diff = c_list[sta] * 0.5 / min_lever
    cal_max, cal_min = max(h_list[:sta+1]), min(l_list[:sta+1])
    xnum = h_list[:sta+1].index(cal_max)
    nnum = l_list[:sta+1].index(cal_min)
    cal_diff = cal_max - cal_min
    cal_lever = c_list[sta] * 0.5 / cal_diff
    limit_diff = cal_diff
    upper_v, lower_v = 0, 0
    for std in range(sta+1):
            if(c_list[0] > h_list[std]): lower_v = lower_v + v_list[std]
            elif(c_list[0] < l_list[std]): upper_v = upper_v + v_list[std]
            else:
              if(h_list[std] != l_list[std]):
                  upper_v = upper_v + (abs(c_list[0] - h_list[std]) / (h_list[std] - l_list[std]) * v_list[std])
                  lower_v = lower_v + (abs(c_list[0] - l_list[std]) / (h_list[std] - l_list[std]) * v_list[std])
    vol_per = lower_v / (upper_v + lower_v) * 100
    if(order_side == 1) and (vol_per < 75): order_position = 2
    if(order_side == 2) and (vol_per > 25): order_position = 1
    cal_per = round((c_list[0] - cal_min) / (cal_max - cal_min) * 100, 2)
    print(sym_bol, itv, order_position, round(cal_per, 2), round(vol_per, 2))
    limit_diff = cal_diff
    break
#-------------------------------------------------------------------------------
  l_next_price, s_next_price = cal_max, cal_min
  mx_time = float(t_list[xnum] * 0.001)
  mx_server_time = str(datetime.utcfromtimestamp(mx_time) + timedelta(hours=9))
  mn_time = float(t_list[nnum] * 0.001)
  mn_server_time = str(datetime.utcfromtimestamp(mn_time) + timedelta(hours=9))
  s_value_list = [l_next_price, s_next_price, round(cal_per, 2), round(vol_per, 2)]
  v_value_list = [itv, mx_server_time, mn_server_time]
#-------------------------------------------------------------------------------
  order_return = [order_position, limit_diff, s_value_list, v_value_list]
  return(order_return)
################################################################################
###############################################################################
while True:
    # limit_time = int((int(time.time()) - (6 * 24 * 60 * 60)) * 1000)
    # final_time = int((int(time.time()) - (5 * 24 * 60 * 60)) * 1000)
    # 1. 바이낸스 선물 계좌 정보 조회
    account_info = client.futures_account()
    # 잔고 / 자산 / 증거금 관련 항목 매핑
    my_usdt = float(account_info["totalWalletBalance"])  # 지갑 총 잔고 (Total Wallet Balance)
    live_usdt = float(account_info["totalMarginBalance"])  # 미실현 손익 포함 총 평가자산 (Equity)
    tot_position = float(account_info["totalPositionInitialMargin"])  # 포지션 유지 증거금
    total_order_im = float(account_info["totalOpenOrderInitialMargin"])  # 미체결 주문 증거금
    avail_usdt = float(account_info["availableBalance"])  # 주문 가능 잔고 (Available Balance)
    time.sleep(1)

    # 잔고 최고/최저 기록용 변수 세팅 (기존 로직 유지)
    max_l_usdt, min_l_usdt, origin_usdt = live_usdt, live_usdt, my_usdt
    max_m_usdt, min_m_usdt = my_usdt, my_usdt
    max_t_position = tot_position

    try_item = []
    union_list, inter_list, setdf_list = [], [], []
    limit_max_num = my_usdt / invest_usdt

    # 2. 보유 중인 포지션 정보 조회 및 심볼 추출
    positions = client.futures_position_information()
    time.sleep(1)
    df_positions = pd.DataFrame(positions)
    # positionAmt(수량)가 0이 아닌 포지션만 실제 보유 포지션으로 필터링
    df_positions["positionAmt"] = df_positions["positionAmt"].astype(float)
    active_positions = df_positions[df_positions["positionAmt"] != 0].copy()
    if active_positions.empty:
        long_list, short_list, union_list = [], [], []
    else:
        # Long 포지션: positionAmt > 0 (또는 positionSide == 'LONG')
        long_list = active_positions[active_positions["positionAmt"] > 0]["symbol"].unique().tolist()
        # Short 포지션: positionAmt < 0 (또는 positionSide == 'SHORT')
        short_list = active_positions[active_positions["positionAmt"] < 0]["symbol"].unique().tolist()
        # 전체 보유 포지션 심볼 유니크 리스트
        union_list = active_positions["symbol"].unique().tolist()
    try_list = union_list.copy()
#-------------------------------------------------------------------------------
    l_order_num = len(long_list)
    s_order_num = len(short_list)
    secure_usdt = max(l_order_num, s_order_num) * invest_usdt * 0.5
    avail_order_num = 25 - len(try_list)
#-------------------------------------------------------------------------------
##############################################################################
##############################################################################
# --- 기존 루프 내 변수 선언 영역 ---
    ordered_item = 25
    wish_item_no = 100
# 조건 만족 시 실행
    if (avail_order_num > 0) and (ordered_item > len(try_list)):
        # 1. 바이낸스 선물 24시간 티커 데이터 조회
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
        sort_list = df.sort_values('turnover24h', key=lambda x: x.abs(), ascending=False, ignore_index=True)
        # 조건 필터링: 현재가가 (invest_usdt * 2) 미만인 종목
        added_list = sort_list[(sort_list['lastPrice'] < (invest_usdt * 2))]
        added_symbols = added_list["symbol"].tolist()
        # -------------------------------------------------------------------------
        # 2. 바이낸스 상장 폐지 / 거래 정지 심볼 제외 로직
        # -------------------------------------------------------------------------
        final_del_list = []
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
        print('added_symbols (최종 추가):', len(added_symbols))
#-------------------------------------------------------------------------------
    try_item = try_list.copy()
    print('try_item:',len(try_item))
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
    if(try_item != []):  
        last_time = int(time.time())
        num = 0
###############################################################################
        for sym_bol in try_item:
          item_no = try_item.index(sym_bol)
          i_last_time = int(time.time())
          now_time = int(time.time()) * 1000
          apply_time = reset_time
#-------------------------------------------------------------------------------
          order_condition, limit_diff_p = 0, 0
          value_s_list, value_v_list = [], []
###############################################################################
###############################################################################
          # 1. 현재가 조회
          sym_ticker = client.futures_symbol_ticker(symbol=sym_bol)
          sym_price = float(sym_ticker['price'])
          # 2. 포지션 정보 조회
          res_ponse = client.futures_position_information(symbol=sym_bol)
          time.sleep(1)
          df = pd.DataFrame(res_ponse)
# -------------------------------------------------------------------------------
          def clean(x):
              if x is None or str(x).strip() == "" or str(x).strip() == "0":
                  return 0
              return float(x)
# -------------------------------------------------------------------------------
          long_df = df[df['positionSide'] == 'LONG']
          short_df = df[df['positionSide'] == 'SHORT']
          # 만약 One-Way Mode(단방향)인 경우 positionSide가 'BOTH'로 표시될 수 있으므로 예외 처리
          if long_df.empty and short_df.empty:
            # One-way mode 처리
            both_df = df[df['positionSide'] == 'BOTH']
            amt = float(both_df['positionAmt'].values[0]) if not both_df.empty else 0
            long_qty = amt if amt > 0 else 0
            short_qty = abs(amt) if amt < 0 else 0   
            # 공통 항목 추출 헬퍼
            def get_val(df_target, key, default=0):
                return df_target[key].values[0] if not df_target.empty else default
            l_sym_lever = s_sym_lever = get_val(both_df, 'leverage', 1)
            l_ent_price = s_ent_price = clean(get_val(both_df, 'entryPrice'))
            l_unpnl = s_unpnl = clean(get_val(both_df, 'unRealizedProfit'))
            l_position = s_position = clean(get_val(both_df, 'isolatedWallet'))
            l_position_im = s_position_im = clean(get_val(both_df, 'initialMargin'))
            l_created_time = s_created_time = clean(get_val(both_df, 'updateTime'))
            l_liq_price = s_liq_price = clean(get_val(both_df, 'liquidationPrice'))
          else:
            # Hedge Mode (헤지 모드) 기준 데이터 추출
            l_row = long_df.iloc[0] if not long_df.empty else {}
            s_row = short_df.iloc[0] if not short_df.empty else {}
            long_qty = abs(clean(l_row.get('positionAmt', 0)))
            short_qty = abs(clean(s_row.get('positionAmt', 0)))
            l_sym_lever = int(l_row.get('leverage', 1))
            s_sym_lever = int(s_row.get('leverage', 1))
            l_ent_price = clean(l_row.get('entryPrice', 0))
            s_ent_price = clean(s_row.get('entryPrice', 0))
            l_unpnl = clean(l_row.get('unRealizedProfit', 0))
            s_unpnl = clean(s_row.get('unRealizedProfit', 0))
            l_position = clean(l_row.get('isolatedWallet', 0))
            s_position = clean(s_row.get('isolatedWallet', 0))
            l_position_im = clean(l_row.get('initialMargin', 0))
            s_position_im = clean(s_row.get('initialMargin', 0))
            l_created_time = clean(l_row.get('updateTime', 0))
            s_created_time = clean(s_row.get('updateTime', 0))
            l_liq_price = clean(l_row.get('liquidationPrice', 0))
            s_liq_price = clean(s_row.get('liquidationPrice', 0))
          # 1. 포지션 기본 정보 가져오기
          res_ponse = client.futures_position_information(symbol=sym_bol)
          # 2. 손절가(Stop Loss) 조회를 위한 미체결 스탑 주문 확인
          open_orders = client.futures_get_open_orders(symbol=sym_bol)
          l_st_loss = 0
          s_st_loss = 0
          for order in open_orders:
            if order['type'] in ['STOP_MARKET', 'STOP']:
                pos_side = order.get('positionSide', 'BOTH')
                if pos_side == 'LONG': l_st_loss = float(order['stopPrice'])
                elif pos_side == 'SHORT': s_st_loss = float(order['stopPrice'])
                elif pos_side == 'BOTH':
                    if order['side'] == 'SELL': l_st_loss = float(order['stopPrice'])
                    elif order['side'] == 'BUY': s_st_loss = float(order['stopPrice'])    
        
          # 3. 심볼 규격 정보 (Instruments Info / Exchange Info) 조회
          exchange_info = client.futures_exchange_info()
          info = next((item for item in exchange_info['symbols'] if item['symbol'] == sym_bol), None)
          if info:
            status = info['status']
            # 필터 목록 구조 파싱 (LOT_SIZE, PRICE_FILTER, MIN_NOTIONAL 등)
            filters = {f['filterType']: f for f in info['filters']}
            # 수량 관련 단위 및 최소 주문 수량 (LOT_SIZE)
            lot_filter = filters.get('LOT_SIZE', {})
            qty_step = float(lot_filter.get('stepSize', 0))
            min_qty = float(lot_filter.get('minQty', 0))
            # 최소 주문 금액 (MIN_NOTIONAL)
            notional_filter = filters.get('MIN_NOTIONAL', {})
            min_value = float(notional_filter.get('notional', 0))
            # 가격 최소 변화 단위 (PRICE_FILTER)
            price_filter = filters.get('PRICE_FILTER', {})
            tick_size = float(price_filter.get('tickSize', 0))
            
          # 심볼별 레버리지 브래킷(Bracket) 정보 조회
          brackets = client.futures_leverage_bracket(symbol=sym_bol)
          # 첫 번째 브래킷(가장 적은 금액 구간)의 initialLeverage가 해당 심볼의 최대 레버리지입니다.
          max_leverage = brackets[0]['brackets'][0]['initialLeverage']
          max_lever = max_leverage
          min_lever = 1
          lever_step = 1

          # 1. 바이낸스 선물 계좌 정보 조회
          account_info = client.futures_account()
          # 잔고 / 자산 / 증거금 관련 항목 매핑
          my_usdt = float(account_info["totalWalletBalance"])  # 지갑 총 잔고 (Total Wallet Balance)
          live_usdt = float(account_info["totalMarginBalance"])  # 미실현 손익 포함 총 평가자산 (Equity)
          tot_position = float(account_info["totalPositionInitialMargin"])  # 포지션 유지 증거금
          total_order_im = float(account_info["totalOpenOrderInitialMargin"])  # 미체결 주문 증거금
          avail_usdt = float(account_info["availableBalance"])  # 주문 가능 잔고 (Available Balance)
          time.sleep(1)
##############################################################################
##############################################################################
          # 1. 바이낸스 선물 계좌 체결 내역 조회 (최근 10건, start_time 기준)
          res = client.futures_account_trades(symbol=sym_bol, startTime=start_time, limit=10)
          last_trade = pd.DataFrame(res)
          if last_trade.empty:
            created_time, exec_price, trade_side, trade_type = 0, 0, "None", "None"
          else:
            # 체결 시간(time) 기준 내림차순 정렬 (가장 최근 체결이 맨 위로 오도록)
            last_trade = last_trade.sort_values("time", ascending=False)
            # 가장 최근 체결 데이터 1건 추출
            recent = last_trade.iloc[0]
            created_time = int(recent["time"])
            exec_price = float(recent["price"])
            # 매수/매도 방향 판단 (buyer 가 True면 Buy, False면 Sell)
            if "buyer" in recent:
                trade_side = "Buy" if recent["buyer"] else "Sell"
            else:
                trade_side = recent.get("side", "None")
            # 바이낸스 체결 내역은 주문 타입(Maker/Taker 여부만 제공)을 직접 구별해주지 않으므로 기본값 또는 maker 여부 저장
            trade_type = "Maker" if recent.get("maker", False) else "Taker"
##############################################################################
##############################################################################
          # 1. 바이낸스 선물 계좌 체결 내역 조회 (startTime 이후)
          res_pnl = client.futures_account_trades(symbol=sym_bol, startTime=start_time, limit=50)
          df_trades = pd.DataFrame(res_pnl)
          if df_trades.empty:
                closed_pnl = pd.DataFrame()
          else:
                # realizedPnl(실현손익) 컬럼을 float로 변환
                df_trades["realizedPnl"] = df_trades["realizedPnl"].astype(float)
                # 포지션 청산으로 실현 손익이 발생한 체결건(realizedPnl != 0)만 필터링
                closed_pnl = df_trades[df_trades["realizedPnl"] != 0].copy()
          if closed_pnl.empty:
                last_pnl = 0
                last_side = "None"
                (
                    closed_time,
                    closed_side_str,
                    pnl_list,
                    avg_entry_price,
                    avg_exit_price,
                ) = ([], [], [], [], [])
          else:
                # 체결 시간(time) 기준 내림차순 정렬 (가장 최근 청산건이 0번 인덱스)
                closed_pnl = closed_pnl.sort_values("time", ascending=False)
                # 1) 가장 최근 청산 손익 및 방향
                last_pnl = float(closed_pnl.iloc[0]["realizedPnl"])
                # 포지션 방향 파악 (positionSide가 있으면 우선 사용, 없으면 buyer/side로 판단)
                first_row = closed_pnl.iloc[0]
                if "positionSide" in first_row and first_row["positionSide"] != "BOTH":
                    last_side = ("Sell" if first_row["positionSide"] == "LONG" else "Buy")  # Long 청산은 Sell
                else:
                    last_side = "Sell" if first_row.get("buyer", False) else "Buy"
                # 2) 리스트 형태 추출
                closed_time = closed_pnl["time"].astype(int).tolist()
                pnl_list = closed_pnl["realizedPnl"].astype(float).tolist()
                # 청산 체결가 (바이낸스 체결 단가)
                avg_exit_price = closed_pnl["price"].astype(float).tolist()
                # 바이낸스 Trade API는 개별 진입 평단가를 별도로 리턴하지 않으므로 exit price로 대체하거나 0 처리
                avg_entry_price = [0.0] * len(closed_pnl)
                # 방향 리스트 (Buy/Sell)
                if "positionSide" in closed_pnl.columns:
                    closed_side_str = ["Sell" if ps == "LONG" else "Buy" for ps in closed_pnl["positionSide"]]
                else:
                    closed_side_str = ["Buy" if b else "Sell" for b in closed_pnl["buyer"]]
##############################################################################
##############################################################################
          # 기본 변수 초기화
          apply_time = created_time
          apply_price = exec_price
          entry_price, exit_price = 0, 0
          accum_num, accum_pnl = 0, 0
          order_index = -1
          filtered_pri, entry_p_list, exit_p_list = [], [], []
          try:
            # 1. 바이낸스 선물 주문 내역 조회 (startTime 이후 주문 최대 20건)
            res_order = client.futures_get_all_orders(symbol=sym_bol, startTime=start_time, limit=20)
            order_history = pd.DataFrame(res_order)
            if order_history.empty:
                open_time, open_side, open_linkid = [], [], []
            else:
                # bool/str 타입 컬럼 정리
                order_history["reduceOnly"] = order_history["reduceOnly"].astype(bool)
                # 2. 신규 진입 주문(Open) 조건 필터링
                # - reduceOnly가 False
                # - 체결 완료(FILLED) 또는 부분 체결(PARTIALLY_FILLED)
                # - 바이낸스는 type 컬럼으로 LIMIT, MARKET, STOP_MARKET 등을 통합 관리
                order_open = order_history[
                    (order_history["reduceOnly"] == False)
                    & (
                        order_history["status"].isin(["FILLED", "PARTIALLY_FILLED"])
                    )
                ].copy()
                if order_open.empty:
                    open_time, open_side, open_linkid = [], [], []
                else:
                    # updateTime 기준 내림차순 정렬
                    order_open = order_open.sort_values("updateTime", ascending=False)
                    open_time = order_open["updateTime"].astype(int).tolist()
                    open_side = order_open["side"].tolist()  # 'BUY' 또는 'SELL'
                    # 바이낸스는 orderLinkId 대신 clientOrderId를 사용합니다.
                    open_linkid = order_open["clientOrderId"].tolist()
                    # 'First' 문구가 clientOrderId에 포함된 최신 주문의 인덱스 탐색
                    order_index = next((i for i, x in enumerate(open_linkid) if "First" in str(x)), -1)
                    if order_index == -1:
                        apply_time = created_time
                        apply_price = exec_price
                        accum_num, accum_pnl = 0, 0
                    else:
                        apply_time = open_time[order_index]
                        accum_num = order_index
                        # 이전 Step에서 추출한 closed_time, pnl_list 활용
                        filtered_pnl = [p for t, p in zip(closed_time, pnl_list) if t >= apply_time]
                        accum_pnl = sum(filtered_pnl)
                        entry_p_list = [p for t, p in zip(closed_time, avg_entry_price) if t >= apply_time]
                        if not entry_p_list:
                            apply_price, entry_price = exec_price, 0
                        else:
                            apply_price, entry_price = entry_p_list[-1], entry_p_list[-1]
                        exit_p_list = [p for t, p in zip(closed_time, avg_exit_price) if t >= apply_time]
                        if not exit_p_list: exit_price = 0
                        else:  exit_price = exit_p_list[-1]
          except Exception as e:
            print("order_history API error:", e)
            # continue  # 루프 내부일 경우 예외 처리
##############################################################################
##############################################################################
#-------------------------------------------------------------------------------
          if(entry_price == 0) and (exit_price == 0):
            if(long_qty != 0): entry_price, exit_price = float(l_ent_price), float(l_st_loss)
            if(short_qty != 0): entry_price, exit_price = float(s_ent_price), float(s_st_loss)
          diff_gap = Decimal(str(abs(entry_price - exit_price))) / Decimal(tick_size)
          diff_gap = float(int(diff_gap) * Decimal(tick_size))
#-------------------------------------------------------------------------------
          # 기본 배열 초기화
          m_order_idx = [0, 0, 0]
          m_order_tp = [0, 0, 0]
          m_order_st = [0, 0, 0]
          m_order_qty = [0, 0, 0]
          try:
            # 1. 바이낸스 선물 미체결 주문 조회
            res_orders = client.futures_get_open_orders(symbol=sym_bol)
            open_orders = pd.DataFrame(res_orders)
            if open_orders.empty:
                limit_order_list = []
                stop_order_list = []
                trail_item = 0
            else:
                # 바이낸스는 모든 주문 타입이 'type' 컬럼 하나로 관리됩니다.
                limit_order_list = open_orders["type"].tolist()
                stop_order_list = open_orders["type"].tolist()
                # 트레일링 스탑 주문 존재 여부 확인 (바이낸스 주문 타입: TRAILING_STOP_MARKET)
                if "TRAILING_STOP_MARKET" in stop_order_list:
                    trail_item = 1
                else:
                    trail_item = 0
                # 조건부 스탑 주문 필터링 (STOP_MARKET, STOP, TAKE_PROFIT_MARKET 등)
                stop_df = open_orders[open_orders["type"].isin(["STOP_MARKET", "STOP"])].copy()
                if not stop_df.empty:
                    # 1) 헤지 모드(Hedge Mode) 기준 포지션 분기 (LONG / SHORT)
                    long_row = stop_df[stop_df["positionSide"] == "LONG"]
                    short_row = stop_df[stop_df["positionSide"] == "SHORT"]
                    # 2) 단방향 모드(One-Way Mode)인 경우 positionSide가 'BOTH'이므로 side(BUY/SELL)로 구분
                    if long_row.empty and short_row.empty:
                        # Long 포지션의 스탑 주문은 보통 SELL 방향
                        long_row = stop_df[stop_df["side"] == "SELL"]
                        # Short 포지션의 스탑 주문은 보통 BUY 방향
                        short_row = stop_df[stop_df["side"] == "BUY"]
                    # Long 스탑 주문 파싱 (인덱스 1)
                    if not long_row.empty:
                        l_item = long_row.iloc[0]
                        m_order_idx[1] = 1
                        # 바이낸스 스탑 주문의 발동 가격은 stopPrice
                        m_order_tp[1] = float(l_item.get("stopPrice", 0))
                        m_order_st[1] = float(l_item.get("stopPrice", 0))
                        m_order_qty[1] = float(l_item.get("origQty", 0))
                    # Short 스탑 주문 파싱 (인덱스 2)
                    if not short_row.empty:
                        s_item = short_row.iloc[0]
                        m_order_idx[2] = 2
                        m_order_tp[2] = float(s_item.get("stopPrice", 0))
                        m_order_st[2] = float(s_item.get("stopPrice", 0))
                        m_order_qty[2] = float(s_item.get("origQty", 0))
          except Exception as e:
            print("open_orders API error:", e)
            limit_order_list = []
            stop_order_list = []
            trail_item = 0
##############################################################################
##############################################################################
# ------------------------------------------------------------------
# 메인 조건 판단 및 손절가 계산 로직 (바이낸스 호환)
# ------------------------------------------------------------------
        # Long 포지션 리스크 관리
          if (long_qty != 0) and (float(l_st_loss) != 0) and (float(l_liq_price) >= float(l_st_loss)):
            # 진입가와 강제청산가 차이의 80% 지점으로 계산
            c_ex_st_loss = str(float(l_ent_price) - (abs(float(l_ent_price) - float(l_liq_price)) * 0.8))
            # Tick Size 단위 반영 (Decimal 양자화 / 호가단위 버림 처리)
            c_st_loss = str((Decimal(c_ex_st_loss) // Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, c_st_loss, 1]
            set_stop_loss_item(add_order)
            print(sym_bol, "L_set_stop_loss")
            continue
        # Short 포지션 리스크 관리
          if (short_qty != 0) and (float(s_st_loss) != 0)  and (float(s_liq_price) <= float(s_st_loss)):
            c_ex_st_loss = str(float(s_ent_price) + (abs(float(s_ent_price) - float(s_liq_price)) * 0.8))
            # Tick Size 단위 반영
            c_st_loss = str((Decimal(c_ex_st_loss) // Decimal(tick_size)) * Decimal(tick_size))
            add_order = [sym_bol, c_st_loss, 2]
            set_stop_loss_item(add_order)
            print(sym_bol, "S_set_stop_loss")
            continue
##############################################################################
##############################################################################
          order_side = 0
          if(long_qty != 0):  order_side = 1
          if(short_qty != 0): order_side = 2
          if(long_qty == 0) and (short_qty == 0):
              search_calc_result = search_calc(sym_bol, accum_num)
              order_condition = search_calc_result[0]
              limit_diff_p = search_calc_result[1]
              value_s_list = search_calc_result[2]
              value_v_list = search_calc_result[3]
          else:
              order_calc_result = order_calc(sym_bol, apply_time, order_side)
              order_condition = order_calc_result[0]
              limit_diff_p = order_calc_result[1]
              value_s_list = order_calc_result[2]
              value_v_list = order_calc_result[3]
          h_price, l_price = sym_price, sym_price
          max_diff = sym_price * 0.5 / 5
          if(limit_diff_p > max_diff): limit_diff_p = max_diff
#-------------------------------------------------------------------------------
#START
#-------------------------------------------------------------------------------
          if(try_item != []):  
#-------------------------------------------------------------------------------
# 기본 변수 설정
            lever_check = 0
            m_lever = 5
            try:
                # 조건 만족 시 레버리지 계산 진행
                if (order_condition in (1, 2, 3, 4)) and (value_s_list[2] < float(max_lever)):
                    # 동적 레버리지 및 최소 레버리지(m_lever) 산출
                    if value_s_list[2] > m_lever: str_lever = str(value_s_list[2])
                    else: str_lever = str(m_lever)
                    # Step 단위 정밀도 연산 (몫 연산자 // 사용)
                    apply_lever = str(int((Decimal(str_lever) // Decimal(lever_step)) * Decimal(lever_step)))
                    target_lever = float(apply_lever)
                    # ------------------------------------------------------------------
                    # 1. 레버리지 변경 요청
                    # ------------------------------------------------------------------
                    # 바이낸스는 Buy/Sell 분리가 없으므로 심볼 전체에 target_lever를 적용합니다.
                    # Case A: 무포지션 상태
                    if (long_qty == 0) and (short_qty == 0):
                        if (float(l_sym_lever) != target_lever) or (float(s_sym_lever) != target_lever):
                            client.futures_change_leverage(symbol=sym_bol, leverage=int(target_lever))
                            time.sleep(1)
                            lever_check = 3
                    # ------------------------------------------------------------------
                    # 2. 레버리지 변경 후 포지션 재조회 및 검증
                    # ------------------------------------------------------------------
                    if lever_check == 3:
                        res_ponse = client.futures_position_information(symbol=sym_bol)
                        time.sleep(1)
                        # 바이낸스 포지션 내역 파싱 (LONG / SHORT 또는 BOTH)
                        df_pos = pd.DataFrame(res_ponse)
                        if not df_pos.empty:
                            # 헤지 모드(Hedge Mode) 기준
                            long_pos = df_pos[df_pos["positionSide"] == "LONG"]
                            short_pos = df_pos[df_pos["positionSide"] == "SHORT"]
                            if not long_pos.empty and not short_pos.empty:
                                l_sym_lever = float(long_pos.iloc[0]["leverage"])
                                s_sym_lever = float(short_pos.iloc[0]["leverage"])
                            else:
                                # 단방향 모드(One-Way Mode)인 경우 BOTH 하나의 레버리지 적용
                                l_sym_lever = float(df_pos.iloc[0]["leverage"])
                                s_sym_lever = float(df_pos.iloc[0]["leverage"])
                    # ------------------------------------------------------------------
                    # 3. 최종 반영 상태 플래그 검증 (lever_check = 1)
                    # ------------------------------------------------------------------
                    if (long_qty == 0) and (short_qty == 0):
                        if (float(l_sym_lever) == target_lever) and (float(s_sym_lever) == target_lever):
                            lever_check = 1
            except Exception as e:
                print(f"[{sym_bol}] leverage update error:", e)
                lever_check = 0
##############################################################################
##############################################################################
#-------------------------------------------------------------------------------
            if(long_qty == 0) and (short_qty == 0) and (order_condition in (1, 2, 3, 4)) and (lever_check == 1): num = num + 1
#-------------------------------------------------------------------------------
    #         max_ls_usdt = invest_usdt * (2 ** (retry_num))
    #         add_invest_usdt = invest_usdt * (2 ** (accum_num + 0))
    #         if((add_invest_usdt * 1) > avail_usdt):
    #           add_invest_usdt = invest_usdt
    #         if(order_index not in (1, 2)):
    #           add_invest_usdt = invest_usdt
    #         if(long_qty == 0) and (short_qty == 0) and (accum_pnl >= 0):
    #           add_invest_usdt = invest_usdt
            add_invest_usdt = invest_usdt
#-------------------------------------------------------------------------------
            l_ex_price = str(h_price - float(tick_size))
            l_order_price = str(int(Decimal(l_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            l_ex_qty = str((add_invest_usdt * float(l_sym_lever)) / float(l_order_price))
            l_order_qty = str(int(Decimal(l_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
            l_tp_ex_price = str(0)
    #        l_tp_ex_price = str(h_price + (limit_diff_p * 1.3) + float(tick_size))
            l_tp_price = str(int(Decimal(l_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            l_st_ex_price = str(h_price - limit_diff_p - float(tick_size))
            l_st_price = str(int(Decimal(l_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            l_order_side = 'Buy'
            l_order_position = 1
            l_ex_value = float(l_order_qty) * float(l_order_price) * 1.0
            l_ex_st_per = (abs(float(l_order_price) - float(l_st_price)) * float(l_sym_lever)) / float(l_order_price)
    
            s_ex_price = str(l_price + float(tick_size))
            s_order_price = str(int(Decimal(s_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            s_ex_qty = str((add_invest_usdt * float(s_sym_lever)) / float(s_order_price))
            s_order_qty = str(int(Decimal(s_ex_qty) / Decimal(qty_step)) * Decimal(qty_step))
            s_tp_ex_price = str(0)
    #        s_tp_ex_price = str(l_price - (limit_diff_p * 1.3) - float(tick_size))
    #        if(float(s_tp_ex_price) < (l_price * 0.15)): s_tp_ex_price = str(l_price * 0.15)
            s_tp_price = str(int(Decimal(s_tp_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            s_st_ex_price = str(l_price + limit_diff_p + float(tick_size))
            s_st_price = str(int(Decimal(s_st_ex_price) / Decimal(tick_size)) * Decimal(tick_size))
            s_order_side = 'Sell'
            s_order_position = 2
            s_ex_value = float(s_order_qty) * float(s_order_price) * 1.0
            s_ex_st_per = (abs(float(s_order_price) - float(s_st_price)) * float(s_sym_lever)) / float(s_order_price)
##############################################################################
#-----------------------------------------------------------------------------
            if(order_condition not in (100, 900)):
#-----------------------------------------------------------------------------
##############################################################################
                # 1. Long 신규 진입 (order_condition 1, 3)
                if (order_condition in (1, 3)) and (lever_check == 1):
                    if ((long_qty == 0) and (short_qty == 0) and ((add_invest_usdt * 2) < avail_usdt) and (avail_order_num >= num)):
                        if float(max_lever) >= float(l_sym_lever):
                            if (float(min_value) < l_ex_value) and (float(l_order_qty) != 0):
                                # 바이낸스 newClientOrderId 규칙에 맞춘 주문 ID 생성
                                order_linkid = f"{sym_bol}_First_L_{int(time.time()*1000)}"
                                # 바이낸스는 대문자 'BUY' 사용
                                add_order = [sym_bol, "BUY", l_order_qty, 1, l_tp_price, l_st_price, order_linkid]
                                order_market_part(add_order)
                                time.sleep(1)
                # 2. Short 신규 진입 (order_condition 2, 4)
                if (order_condition in (2, 4)) and (lever_check == 1):
                    if ((long_qty == 0) and (short_qty == 0) and ((add_invest_usdt * 2) < avail_usdt) and (avail_order_num >= num)):
                        if float(max_lever) >= float(s_sym_lever):
                            if (float(min_value) < s_ex_value) and (float(s_order_qty) != 0):
                                order_linkid = f"{sym_bol}_First_S_{int(time.time()*1000)}"
                                # 바이낸스는 대문자 'SELL' 사용
                                add_order = [sym_bol, "SELL", s_order_qty, 2, s_tp_price, s_st_price, order_linkid]
                                order_market_part(add_order)
                                time.sleep(1)
##############################################################################
##############################################################################
            # 1. Long 포지션 청산 조건
            if long_qty != 0:
                # 시간 제한 1차 Over
                if (created_time != 0) and (apply_time < limit_time):
                    add_order = [sym_bol, "SELL", 1]
                    closed_order_part(add_order)
                    time.sleep(1)
                    # 바이낸스 미체결/TP/SL 취소
                    cancel_all_orders(sym_bol)
                    time.sleep(1)
                    print(sym_bol, "L_limit_time OVER")
                # 시간 제한 Final Over & 최소 수익 조건
                if ((created_time != 0) and (apply_time < final_time) and (float(l_unpnl) > (invest_usdt * 0.1))):
                    add_order = [sym_bol, "SELL", 1]
                    closed_order_part(add_order)
                    time.sleep(1)
                    cancel_all_orders(sym_bol)
                    time.sleep(1)
                    print(sym_bol, "L_final_time OVER")
            
                # 반대 신호(2번) 발생 및 TP 조건 만족
                if (order_condition == 2) and (float(l_unpnl) > (invest_usdt * 0.375)):
                    add_order = [sym_bol, "SELL", 1]
                    closed_order_part(add_order)
                    time.sleep(1)
                    cancel_all_orders(sym_bol)
                    time.sleep(1)
                    print(sym_bol, "L_order_condition_end")
            
            # 2. Short 포지션 청산 조건
            if short_qty != 0:
                # 시간 제한 1차 Over
                if (created_time != 0) and (apply_time < limit_time):
                    add_order = [sym_bol, "BUY", 2]
                    closed_order_part(add_order)
                    time.sleep(1)
                    cancel_all_orders(sym_bol)
                    time.sleep(1)
                    print(sym_bol, "S_limit_time OVER")
                # 시간 제한 Final Over & 최소 수익 조건
                if ((created_time != 0) and (apply_time < final_time) and (float(s_unpnl) > (invest_usdt * 0.1))):
                    add_order = [sym_bol, "BUY", 2]
                    closed_order_part(add_order)
                    time.sleep(1)
                    cancel_all_orders(sym_bol)
                    time.sleep(1)
                    print(sym_bol, "S_final_time OVER")
                # 반대 신호(1번) 발생 및 TP 조건 만족
                if (order_condition == 1) and (float(s_unpnl) > (invest_usdt * 0.375)):
                    add_order = [sym_bol, "BUY", 2]
                    closed_order_part(add_order)
                    time.sleep(1)
                    cancel_all_orders(sym_bol)
                    time.sleep(1)
                    print(sym_bol, "S_order_condition_end")
    ###############################################################################
            current_apply_time = datetime.fromtimestamp(int(apply_time / 1000)) + timedelta(hours=9)
            if(created_time != 0): trade_time = datetime.fromtimestamp(int(created_time / 1000)) + timedelta(hours=9)
            else: trade_time = 0
            if(long_qty != 0) and (short_qty != 0):
              print(sym_bol,sym_price, 'order_condition:',order_condition,'l_unpnl:',l_unpnl,'s_unpnl:',s_unpnl)
            elif(long_qty == 0) and (short_qty != 0):
              print(sym_bol,sym_price, 'order_condition:',order_condition,'s_unpnl:',s_unpnl,'s_liq_price:',s_liq_price,'invest_usdt:',add_invest_usdt)
            elif(long_qty != 0) and (short_qty == 0):
              print(sym_bol,sym_price, 'order_condition:',order_condition,'l_unpnl:',l_unpnl,'l_liq_price:',l_liq_price,'invest_usdt:',add_invest_usdt)
            else:
              print(sym_bol,sym_price,'order_condition:',order_condition, 'PASS')
            print('value_s:',value_s_list)
            print('value_v:',value_v_list)
            print('accum_num:', accum_num, 'accum_pnl:', accum_pnl, 'apply_price:', apply_price, 'apply_time:', current_apply_time)
            print('order_index:', order_index, 'last_side:', last_side)
            print('last_pnl:', last_pnl, 'diff_gap:', diff_gap, 'trade_time:', trade_time)
######## #######################################################################
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
