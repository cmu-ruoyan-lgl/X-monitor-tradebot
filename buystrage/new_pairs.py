import asyncio
import json
import random
import time

import requests

from buystrage.twitter_strage import get_community_popularity_for_newpair
from mangodb_ops.orm_ops import save_limit_order
from mangodb_ops.ormmapper import new_pair, orders, new_pair_from_gmgn
from soltradebot.tradebot import JupiterWallet

NEW_PAIRS_URL="https://gmgn.ai/defi/quotation/v1/pairs/sol/new_pairs?limit=10&orderby=open_timestamp&direction=desc&filters[]=not_honeypot&created=5m"
QUOTA_TOKEN_URL="https://gmgn.ai/defi/quotation/v1/tokens/sol/"


LANCHPADS = ["Pump.fun"]
class New_Pair_Strage(object):
    def __init__(self, url:str, tradebot:JupiterWallet) -> None:
        super().__init__()
        self.new_pair_url = url
        self.trade_bot = tradebot
        self.new_pairs_queue = asyncio.Queue()

    def get_token_quota(self, ca:str):
        url = QUOTA_TOKEN_URL + ca
        rsp = requests.get(url=url)
        data = json.loads(rsp.text)["data"]["token"]
        return data


    def _get_new_pairs(self) -> []:
        rsp = requests.get(url=self.new_pair_url)
        data = json.loads(rsp.text)["data"]
        pairs = data["pairs"]
        print(pairs)

        new_pairs_from_web = []
        for pair in pairs:
            cur_time = int(time.time())
            # print("since time:")
            # print(cur_time - 50)
            if pair["open_timestamp"] < cur_time - 50:
                continue
            socil_link = []
            if pair["base_token_info"].get("social_links"):
                socil_link = [pair["base_token_info"]["social_links"]["twitter_username"], pair["base_token_info"]["social_links"]["website"], pair["base_token_info"]["social_links"]["telegram"]]

            if pair["launchpad"] in LANCHPADS:
                n = new_pair_from_gmgn(gmgn_id=pair["id"], address=pair["address"], base_address=pair["base_address"], quote_address=pair["quote_address"], liquidity=pair["liquidity"],
                         quote_reserve=pair["quote_reserve"], initial_liquidity=pair["initial_liquidity"], initial_quote_reserve=pair["initial_quote_reserve"],
                         creation_timestamp=pair["creation_timestamp"], quote_reserve_usd=pair["quote_reserve_usd"], burn_ratio=pair["burn_ratio"], burn_status=pair["burn_status"],
                         symbol=pair["base_token_info"]["symbol"], name=pair["base_token_info"]["name"],
                         swaps_1h=pair["base_token_info"]["swaps_1h"], price=pair["base_token_info"]["price"], price_change_percent1m=pair["base_token_info"]["price_change_percent1m"],
                         price_change_percent5m=pair["base_token_info"]["price_change_percent5m"], price_change_percent1h=pair["base_token_info"]["price_change_percent1h"], pool_id=pair["base_token_info"]["pool_id"],
                         is_honeypot=pair["base_token_info"]["is_honeypot"], renounced=pair["base_token_info"]["renounced"], renounced_mint=pair["base_token_info"]["renounced_mint"],
                         social_links=socil_link, market_cap=pair["base_token_info"]["market_cap"], launchpad=pair["launchpad"])
                new_pairs_from_web.append(n)

        return new_pairs_from_web

    def _filter_new_pairs(self, new_pairs:[new_pair_from_gmgn]) ->[]:
        #dev 白名称、黑名单

        pairs = []
        for p in new_pairs:
            tw_username = p.social_links[0] if p.social_links else None
            score = 0
            if tw_username:
                score = get_community_popularity_for_newpair(p.base_address, tw_username)
            print("[coin:{0} | score:{1}]".format(p.symbol, score))

            if score < 60:
                print("[coin:{0} tokenaddress:{2}| score:{1}], skip to buy".format(p.symbol, score, p.base_address))
                continue

            #1. calculate how much to buy
            amount = (int(score / 60) * p.buy_amount)
            p.buy_amount = (amount, 0.1)[amount > 0.1]
            pairs.append(p)

            #2.get decimical

            # record db
            n = new_pair(gmgn_id=p.gmgn_id, address=p.address, base_address=p.base_address,
                                   quote_address=p.quote_address, liquidity=p.liquidity,
                                   base_reserve=p.base_reserve,
                                   quote_reserve=p.quote_reserve, initial_liquidity=p.initial_liquidity,
                                   initial_base_reserve=p.initial_base_reserve,
                                   initial_quote_reserve=p.initial_quote_reserve,
                                   creation_timestamp=p.creation_timestamp,
                                   quote_reserve_usd=p.quote_reserve_usd, burn_ratio=p.burn_ratio,
                                   burn_status=p.burn_status,
                                   symbol=p.symbol, name=p.name,
                                   swaps_1h=p.swaps_1h, price=p.price,
                                   price_1m=p.price_1m,
                                   price_5m=p.price_5m,
                                   price_1h=p.price_1m,
                                   buys_1h=p.buys_1h,
                                   sells_1h=p.sells_1h,
                                   price_change_percent1m=p.price_change_percent1m,
                                   price_change_percent5m=p.price_change_percent5m,
                                   price_change_percent1h=p.price_change_percent1h,
                                   pool_id=p.pool_id,
                                   is_honeypot=p.is_honeypot,
                                   renounced=p.renounced,
                                   renounced_mint=p.renounced_mint,
                                   social_links=p.social_links, market_cap=p.market_cap,
                                   launchpad=p.launchpad, social_score=score).save()
        return pairs

    def get_filter_new_pairs(self):
        new_ps = self._get_new_pairs()
        return self._filter_new_pairs(new_ps)

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
            for new_pair in new_pairs_from_pump:
                print("new pair to buy:")
                print(new_pair.symbol + " : "+new_pair.base_address)
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
            new_pair_strage = New_Pair_Strage(url=NEW_PAIRS_URL, tradebot=jup)
            asyncio.run(new_pair_strage.run_strage())
        except Exception as e:
            print(e)
