import asyncio
import json
import math
import time

import requests

from constant import SOL_TOKEN_ADDRESS, SOL_RPC_URL
from mangodb_ops.orm_ops import save_limit_order, get_all_wallets
from mangodb_ops.ormmapper import limit_orders, user_info, wallet, orders
import mangodb_ops.connect
from soltradebot.tradebot import JupiterWallet
import soltradebot.color_constant as c
from utils.gmgn import get_wallet_profile

TOKEN_PRICE_JUP_API="https://price.jup.ag/v6/price?"
HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

def get_tokenprice_vs_token(token_address, vstoken_address):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    params = {"ids": token_address, "vsToken": vstoken_address}
    respone = requests.get(url=TOKEN_PRICE_JUP_API, params=params, headers=headers)
    if respone.status_code == 200:
        return json.loads(respone.text)["data"]
WALLET={}
def generate_wallet():
    wallets = [{"telegram_id":"6391843369", "private_key":"29LWNpNdnG6nCXvSD9KPAA9KKqwyu8hssBM6s6yFqQ88wJRUUxXpXf4AM6LB9qzHmCYoRzGnuGP8mHvroqwQuDzk"}]
    if wallets:
        for w in wallets:
            jw = JupiterWallet(rpc_url=SOL_RPC_URL, private_key=w["private_key"])
            WALLET.update({w["telegram_id"]: jw})

def get_tokenprice_vs_sol(token_address):
    return get_tokenprice_vs_token(token_address, "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

class OrderBot(object):

    def __init__(self):
        generate_wallet()
        self.token_to_monitor = []
        self.limit_order = []
        self.token_to_monitor_str = ""
        self.update_monitorinfo_time=time.time()
        self.token_price_now = {}
        self.update_monitorinfo()

        self.sell_orders_queue = asyncio.Queue()
        self.still_in_order = []

    #update all date from db
    def update_monitorinfo(self):
        self.limit_order = []
        self.token_to_monitor = []
        self.token_to_monitor_str = ""

        self.limit_order = limit_orders.objects(stat=1)
        for order in self.limit_order:
            self.token_to_monitor.append(order.token_address)
            self.token_to_monitor_str += (order.token_address+",")
        if self.token_to_monitor_str:
            self.token_to_monitor_str = self.token_to_monitor_str[:-1]

    def get_price_of_tm(self):
        self.token_price_now = get_tokenprice_vs_sol(self.token_to_monitor_str)
        return self.token_price_now

    def get_cur_price_by_gmgn(self):
        token_price = []
        for t2, w in WALLET.items():
            profi = get_wallet_profile(str(w.wallet.pubkey()))
            for t in profi:
                if (t["unrealized_pnl"] is not None and  t["unrealized_pnl"] > 0.7 and t["sell_30d"] < 1) or (t["unrealized_pnl"] is not None and t["unrealized_pnl"] > 10):
                    # and t["sell_30d"] < 1
                    token_price.append({"token_address":t["token_address"], "price":t["price"], "amount" :float(t["balance"])/2,"telegram_id": t2, "decimals":t["decimals"]})

        return token_price


    def get_order_sell_from_gmgn(self):
        return self.get_cur_price_by_gmgn()


    def get_limit_order_right(self):
        self.get_cur_price_by_gmgn()
        print(self.token_price_now)
        self.update_monitorinfo()
        limit_order_right = []
        if self.limit_order:
            for lo in self.limit_order:
                if self.token_price_now.get(lo.token_address):
                        if self.token_price_now[lo.token_address][0] >= lo.price:
                            lo.amount = float(self.token_price_now[lo.token_address][1])/2
                            limit_order_right.append(lo)

        return limit_order_right

    async def monitor_limit_order_only_gmgn(self):
        pertime = 30

        while True:
            try:
                await asyncio.sleep(pertime)
                los = self.get_order_sell_from_gmgn()
                print(los)
                for sell_order in los:
                    if sell_order["token_address"] in self.still_in_order:
                        continue
                    # get user wallet and sell order
                    await self.sell_orders_queue.put(sell_order)
            except Exception as e:
                print(e)
                continue

    async def sell_order(self):
        print("start sell order")
        while True:
            try:
                sell_order = await self.sell_orders_queue.get()
                self.still_in_order.append(sell_order["token_address"])
                print("sell_order")
                print(sell_order)
                user_wallet = WALLET[sell_order["telegram_id"]]
                if user_wallet:
                    print("sell limit order")
                    jindu = int(math.pow(10, sell_order["decimals"]))
                    transid = await user_wallet.swap_by_gmgn(buy_token_address=SOL_TOKEN_ADDRESS,sell_token_address=sell_order["token_address"], amount=int(sell_order["amount"]), slippage_bps=10, jindu=jindu)
                    if transid:
                        print(f"{c.GREEN}sell execution success!.{c.RESET}")
                        orders(symbol=sell_order["symbol"], token_address=sell_order["token_address"], stat=1,
                               amount=sell_order["amount"], price=sell_order["price"],
                               tw_user_id="pump", screen_name="pump", direction="sell").save()
                self.still_in_order.remove(sell_order["token_address"])
            except Exception as e:
                self.still_in_order.remove(sell_order["token_address"])
                print(e)
                continue


    async def run_bot(self):
        producer_task = asyncio.create_task(self.monitor_limit_order_only_gmgn())
        consumer_tasks = [asyncio.create_task(self.sell_order()) for _ in range(10)]

        await asyncio.gather(*consumer_tasks, producer_task)
        # 等待队列中的所有任务完成
    async def monitor_limit_order(self):
        pertime = 60

        while True:
            try:
                await asyncio.sleep(pertime)
                los = self.get_limit_order_right()
                print(los)
                for lo in los:

                    # get user wallet and sell order
                    user_wallet = WALLET[lo.telegram_id]
                    if user_wallet:
                        print("sell limit order")
                        transid = await user_wallet.swap_by_gmgn(lo.token_address ,lo.amount,30)
                        if transid:
                            print(f"{c.GREEN}sell execution success!.{c.RESET}")
                            orders(symbol=lo.symbol, token_address=lo.token_address, stat=1, amount=lo.amount, price=lo.price,
                               tw_user_id=lo.tw_user_id, screen_name=lo.screen_name, direction="sell").save()
                            lo.stat=0
                            lo.save()
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    # b = OrderBot()
    # print(b.get_limit_order_right())
    # b.update_monitorinfo()
    # print(b.token_to_monitor_str)
    # print(b.get_price_of_tm())
    # print(b.get_limit_order_right()[0].token_address)
    # # print(get_tokenprice_vs_sol(["SOL","mSOL"]))
    # user = user_info(telegram_id="test", wallet_id="test").save()
    # save_limit_order(symbol="SolTumbler", token_address="HWxrfaRCW7JfqhaKkT9WjD4LnHZg9bncXwXaHbqHD48z", amount=1000, price=0.0000011710213,
    #                  tw_user_id="tweet.user_id", screen_name="tweet.screen_name",
    #                  direction="sell", telegram_id="test")
    # generate_wallet()
    bot = OrderBot()
    print(bot.token_to_monitor_str)
    asyncio.run(bot.run_bot())
