import asyncio
import json
import random
import time

import requests

from buystrage.twitter_strage import get_community_popularity_for_newpair, get_community_popularity_for_newpump, \
    get_tw_view_by_tw_id, get_tw_id_from_twitter_name, get_tw_by_filter_text_twid
from mangodb_ops.orm_ops import save_limit_order
from mangodb_ops.ormmapper import new_pair, orders, new_pair_from_gmgn
from soltradebot.tradebot import JupiterWallet
from utils.time_utils import transfer_time
import soltradebot.color_constant as c

NEW_PUMP_URL= "https://gmgn.ai/defi/quotation/v1/rank/sol/pump?limit=50&orderby=created_timestamp&direction=desc&pump=true&created=5m"
LANCHPADS = ["Pump.fun"]

pumps_monitor = []

class new_pump_from_monitor(object):

    def __init__(self, symbol, base_address, create_timestamp=0, twitter_id=None, ca_tw_id=None, ca_tw_view=None, new_pump=None) -> None:
        super().__init__()
        self.symbol = symbol
        self.create_timestamp = create_timestamp
        self.base_address = base_address
        self.twitter_id = twitter_id
        self.ca_tw_id = ca_tw_id
        self.ca_origin_tw_view = ca_tw_view
        self.ca_pre_view = ca_tw_view
        self.new_pump = new_pump

    def _get_tw_view_newest(self):
        tw_view = get_tw_view_by_tw_id(self.ca_tw_id)
        return tw_view

    def can_buy(self):
        score = 0

        # if tw add before:
        if self.ca_tw_id:
            tw_view = self._get_tw_view_newest(self.ca_tw_id)
            if tw_view > 1000:
                score += 10
                t_c = (tw_view - self.ca_tw_view) / self.ca_tw_view
                if t_c > 10:
                    score += t_c * 30
                t_c = ((tw_view - self.ca_pre_view) / self.ca_pre_view)
                if t_c > 1:
                    score += t_c * 10
            if score > 60:
                return True
        else:
            tw = get_tw_by_filter_text_twid(tw_user_id=self.twitter_id, text=self.base_address)
            if tw:

                self.ca_tw_id = tw.id
                self.create_timestamp = transfer_time(tw.created_at)
                self.ca_pre_view = tw.view_count
                self.ca_origin_tw_view = tw.view_count
        return False

class New_Pair_Strage(object):
    def __init__(self, url:str, tradebot:JupiterWallet) -> None:
        super().__init__()
        self.new_pair_url = url
        self.trade_bot = tradebot
        self.new_pairs_queue = asyncio.Queue()


    def _get_new_pairs(self) -> []:
        rsp = requests.get(url=self.new_pair_url)
        data = json.loads(rsp.text)["data"]
        token_new_pump = data["rank"]
        print(token_new_pump)

        new_pairs_from_web = []
        for pair in token_new_pump:
            cur_time = int(time.time())
            # print("since time:")
            # print(cur_time - 50)
            if pair["created_timestamp"] < cur_time - 60:
                continue
            socil_link = []
            if pair["twitter"]:
                socil_link.append(pair["twitter"])

            n = new_pair_from_gmgn(base_address=pair["address"], creator=pair["creator"], creation_timestamp=pair["created_timestamp"],
                     symbol=pair["symbol"], name=pair["name"],  swaps_1h=pair["swaps_1h"], price=pair["price"], price_change_percent1m=pair["price_change_percent1m"],
                     price_change_percent5m=pair["price_change_percent5m"],social_links=socil_link, market_cap=pair["usd_market_cap"], progress=pair["progress"], holder_count=pair["holder_count"])
            new_pairs_from_web.append(n)

        return new_pairs_from_web

    def _filter_new_pairs(self, new_pairs:[new_pair_from_gmgn]) ->[]:
        #dev 白名称、黑名单

        #twitter 热度
        pairs = []
        for p in new_pairs:
            tw_username = p.social_links[0] if p.social_links else None
            score = 0
            if tw_username:
                score = get_community_popularity_for_newpump(p.base_address, tw_username)


            # record pump to monitor:
            if tw_username:
                user_id = get_tw_id_from_twitter_name(twitter_name=tw_username)
                if user_id:
                    # if had not tw, monitor it
                    tw = get_tw_by_filter_text_twid(tw_user_id=user_id, text=p.base_address)
                    if tw:
                        ca_monitor = new_pump_from_monitor(symbol=p.symbol, create_timestamp=transfer_time(tw.created_at), base_address=p.base_address,
                        twitter_id=user_id, ca_tw_id=tw.id, ca_tw_view=tw.view_count, ca_origin_tw_view=tw.view_count, new_pump=p)
                        pumps_monitor.append(ca_monitor)
                    else:
                        ca_monitor = new_pump_from_monitor(symbol=p.symbol,
                                              base_address=p.base_address,
                                              twitter_id=user_id,
                                              new_pump=p,
                                              create_timestamp=int(time.time()))
                        pumps_monitor.append(ca_monitor)

            print("[coin:{0} | score:{1}]".format(p.symbol, score))
            if score < 1:
                print(f"{c.BLUE}[coin:{p.name} tokenaddress:{p.base_address}| score:{score}], skip to buy {c.RESET}")
                continue

            p.score = score
            amount = (int(score / 60) * p.buy_amount)
            p.buy_amount = (amount, 0.1)[amount > 0.1]
            pairs.append(p)
        return pairs

    def _filter_monitor_pump(self):
        time_elapse = 3600
        pumps = []
        cur_time = int(time.time())
        for pump in pumps_monitor:
            print(f"f{c.BLUE} MONITOR pump:{pump} {c.RESET}")
            if pump.can_buy():
                pumps.append(pump.new_pump)
                pumps_monitor.remove(pump)
                continue
            if cur_time - pump.create_timestamp > time_elapse:
                pumps_monitor.remove(pump)
        return pumps

    def get_filter_new_pairs(self):
        new_pairs = []

        new_ps = self._get_new_pairs()
        new_pairs.extend(self._filter_new_pairs(new_ps))
        new_pairs.extend(self._filter_monitor_pump())
        return new_pairs

    async def run_strage(self):
        producer_task = asyncio.create_task(self.get_new_pairs_to_buy())
        consumer_tasks = [asyncio.create_task(self.buy_new_pair()) for _ in range(10)]

        await producer_task

        # 等待队列中的所有任务完成
        await self.new_pairs_queue.join()
        for task in consumer_tasks:
            task.cancel()

    async def get_new_pairs_to_buy(self):
        while True:
            randomtime = random.randint(30, 60)
            # time.sleep(randomtime)
            await asyncio.sleep(randomtime)
            new_pairs_from_pump = self.get_filter_new_pairs()
            for p in new_pairs_from_pump:
                print("new pair to buy:")
                print(p.symbol + " : " + p.base_address)
                # record db
                n = new_pair(base_address=p.base_address,
                             creator=p.creator, creation_timestamp=p.creation_timestamp,
                             symbol=p.symbol, name=p.name,
                             price=p.price,
                             price_change_percent1m=p.price_change_percent1m,
                             price_change_percent5m=p.price_change_percent5m,
                             social_links=p.social_links, market_cap=p.market_cap,
                             launchpad=p.launchpad, social_score=p.score).save()
                # await self.new_pairs_queue.put(new_pair)

    async def buy_new_pair(self):
        amount = 0.01
        telegram_id = "6391843369"
        while True:
            new_pair = await self.new_pairs_queue.get()
            result = await self.trade_bot.swap_by_gmgn(buy_token_address=new_pair.base_address, amount=amount, slippage_bps=30)
            if result:
                token_account = jup.get_token_mint_account(new_pair.base_address)
                sell_token_account_info = await self.trade_bot.get_token_balance(token_mint_account=token_account)

                amount_to_sell = sell_token_account_info['balance']['float']
                orders(symbol=new_pair.symbol, token_address=new_pair.base_address, stat=1, amount=0.01,
                       price=new_pair.price,
                       screen_name="Pump", direction="buy").save()
                save_limit_order(symbol=new_pair.name, token_address=new_pair.base_address, amount=amount_to_sell / 2,
                                 price=new_pair.price * 2,
                                 direction="sell", telegram_id=telegram_id, tw_user_id="pump", screen_name="pump")



if __name__ == '__main__':
    while True:
        try:
            jup = JupiterWallet(rpc_url="https://api.mainnet-beta.solana.com",
                                private_key="29LWNpNdnG6nCXvSD9KPAA9KKqwyu8hssBM6s6yFqQ88wJRUUxXpXf4AM6LB9qzHmCYoRzGnuGP8mHvroqwQuDzk")
            new_pair_strage = New_Pair_Strage(url=NEW_PUMP_URL, tradebot=jup)
            asyncio.run(new_pair_strage.run_strage())
        except Exception as e:
            print(e)
