import asyncio

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import pytz
import schedule

from telegrambot.telegram_bot_alter import send_message_by_telebot

# 设置东北区时间（UTC+8）
timezone = pytz.timezone("Asia/Shanghai")
coin = []

def get_market_cap(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    market_cap = data[symbol.lower()]["usd"]
    return market_cap

def get_market_cap_CoinGecko(token_id):
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    response = requests.get(url)
    data = response.json()
    if 'market_data' in data and 'market_cap' in data['market_data']:
        return data['market_data']['market_cap']['usd']
    else:
        return None

# 获取所有USDT交易对
def get_all_usdt_pairs():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    df = df[df['symbol'].str.endswith('USDT')]
    df['priceChangePercent'] = df['priceChangePercent'].astype(float)
    return df

# 获取指定交易对在指定时间范围内的交易量
def get_volume_start_end(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,  # 以分钟为间隔获取数据
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000)
    }
    response = requests.get(url, params=params)
    data = response.json()
    volumes = [float(candle[5]) for candle in data]
    return sum(volumes) if volumes else 0

# 获取涨幅榜前100的USDT交易对
def get_top_100_usdt_pairs(usdt_pairs_df):
    top_100_df = usdt_pairs_df.nlargest(10, 'priceChangePercent')
    return top_100_df['symbol'].tolist()


# 获取指定交易对在指定时间范围内的交易量
def get_volume(symbol, interval):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 3  # 获取最近3个15分钟K线
    }
    response = requests.get(url, params=params)
    data = response.json()
    volumes = [float(candle[5]) for candle in data]
    return volumes

def get_all_volumes(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000)
    }
    response = requests.get(url, params=params)
    data = response.json()
    volumes = [float(candle[5]) for candle in data]
    return volumes

def get_pre_month_15m_volumes(symbol):
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone)
    end_time = now - timedelta(hours=1)
    start_time = end_time - timedelta(days=30)
    sum_15m = 2880
    all_volumes = get_all_volumes(symbol, "1d", start_time, end_time)
    if len(all_volumes) == 0:  # 如果前一个月没有交易数据，则跳过
        return 0

    avg_volume_prev_month = sum(all_volumes) / sum_15m
    return avg_volume_prev_month

# 对比每15分钟的交易量，筛选出差距大的交易对
def compare_volumes(pairs):
    results = []

    for symbol in pairs:
        if symbol in coin:
            continue
        try:
            # market_cap = get_market_cap_CoinGecko(symbol)
            # if market_cap < 50000000:
            #     continue
            volumes = get_volume(symbol, "15m")
            if len(volumes) < 3:
                continue
            volume_last_15_min = volumes[1]
            volume_prev_15_min = volumes[0]
            pre_month_15m_volume = get_pre_month_15m_volumes(symbol)
            if volume_prev_15_min == 0:  # Avoid division by zero
                change = float('inf') if volume_last_15_min > 0 else 0
            else:
                change = volume_last_15_min / volume_prev_15_min
                change_vs_premonth = pre_month_15m_volume / volume_prev_15_min

            results.append((symbol, volume_last_15_min, volume_prev_15_min, change, change_vs_premonth))
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    # 筛选出交易量变化大的交易对
    significant_changes = [result for result in results if result[3] > 2 and result[4] > 2]  # 变化超过50%
    significant_changes.sort(key=lambda x: abs(x[3]), reverse=True)
    return significant_changes


# 监控函数
async def monitor():
    usdt_pairs_df = get_all_usdt_pairs()
    top_100_usdt_pairs = get_top_100_usdt_pairs(usdt_pairs_df)
    significant_changes = compare_volumes(top_100_usdt_pairs)

    for change in significant_changes:
        coin.append(change[0])
        print("Symbol: {0}, Last 15m Volume: {1}, Previous 15m Volume: {2}, Change: {3}, change_vs_premonth: {4} ".format(change[0], change[1], change[2], change[3], change[4]))
        # await send_message_by_telebot("6391843369",
        #                               "Symbol: {0}, Last Hour Volume: {1}, Previous Hour Volume: {2}, Change: {3}".format(
        #                                   change[0], change[1], change[2], change[3]))


# 调度函数
async def job():
    print(f"Running monitoring job at {datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')}")
    await monitor()


# 主程序
if __name__ == "__main__":
    # 每15分钟运行
    schedule.every(15).minutes.do(lambda: asyncio.run(job()))

    while True:
        schedule.run_pending()
        time.sleep(1)
    # asyncio.run(job())
    # get_pre_month_15m_volumes("CKBUSDT")
