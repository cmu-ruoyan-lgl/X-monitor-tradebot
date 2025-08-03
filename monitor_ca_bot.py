import asyncio
import time

from constant import SOL_TOKEN_ADDRESS
from mangodb_ops.orm_ops import get_ca_by_address_db, get_tweet_since_time, save_limit_order, get_all_wallets, \
    get_twitter_user
from mangodb_ops.ormmapper import token_info, orders, user_info
import soltradebot.tradebot as tradebot
from telegrambot.telegram_bot_alter import send_message_by_telebot, send_ca_by_telebot
from utils.gmgn import get_token_info, get_tokenprice_vs_sol_by_dexscreen
from utils.regex_utils import find_ca
from decimal import Decimal
import mangodb_ops.connect

#get ca from database and get info from gmgn

# update cache
jup_wallets={}
def get_all_jupwallets():
    wallets = get_all_wallets()
    for wallet in wallets:
        if not jup_wallets.get(wallet.telegram_id):
            jup = tradebot.JupiterWallet(rpc_url="https://api.mainnet-beta.solana.com",
                             private_key=wallet.private_key)
            jup_wallets.update({wallet.telegram_id : jup})

def save_ca_info(CA):
   ca_db = get_ca_by_address_db(CA)
   if ca_db:
       return None
   ca_info = get_token_info(CA)
   print(ca_info)
   if ca_info:
      ti = token_info(chain=ca_info["chain"], symbol=ca_info["symbol"],name=ca_info["name"],decimals=ca_info["decimals"],logo=ca_info["logo"],address=ca_info["address"]
                 ,price=ca_info["price"], price_1h=ca_info["price_1h"],price_24h=ca_info["price_24h"],swaps_5m=ca_info["swaps_5m"],swaps_1h=ca_info["swaps_1h"],volume_24h=ca_info["volume_24h"],liquidity=ca_info["liquidity"],
                 total_supply=ca_info["total_supply"], is_in_token_list=ca_info["is_in_token_list"], hot_level=ca_info["hot_level"], is_honeypot=ca_info["is_honeypot"], renounced=ca_info["renounced"], top_10_holder_rate=ca_info["top_10_holder_rate"]
                 ,renounced_mint=ca_info["renounced_mint"], burn_ratio=ca_info["burn_ratio"], burn_status=ca_info["burn_status"])
      ti.save()
      return ti
   return None

# per minute
async def get_ca_from_tweet(past_time):
    get_all_jupwallets()

    now_time = int(time.time())
    print(now_time - (past_time * 60))
    tweets = get_tweet_since_time(now_time - (past_time * 60))
    print(jup_wallets)
    for tweet in tweets:
        cas = find_ca(tweet.text)
        if cas:
            print("save ca" + cas[0])
            ca = save_ca_info(cas[0])
            if ca:
                amount = 0.01
                tw_user = get_twitter_user(tweet.user_id)
                print("followers:")
                print(tw_user.folloer_ids)
                for flower_id in tw_user.folloer_ids:
                    await send_ca_by_telebot(flower_id, cas[0], tweet)
                    print("new ca:send to {0}".format(flower_id))
                    jup = jup_wallets.get(flower_id)
                    if not jup:
                        continue
                    transid = await jup.swap_by_gmgn(buy_token_address=cas[0], amount=amount, slippage_bps=30)
                    if transid:
                        print("save buy order")
                        pr = ca.price

                        # how to sell in price???
                        token_account = jup.get_token_mint_account(cas[0])
                        sell_token_account_info = await jup.get_token_balance(token_mint_account=token_account)
                        print(sell_token_account_info)
                        # print(pr)
                        #
                        amount_to_sell = sell_token_account_info['balance']['float']
                        #
                        # await jup.dca(sell_token_address=cas[0], buy_token_address=SOL_TOKEN_ADDRESS, amount_to_sell=amount_to_sell/2, prompt_cycle_frequency=10, max_out_amount=float(float(pr) * 2))

                        try:
                        #save order in db
                            orders(symbol=ca.name, token_address=ca.address, stat=1, amount=amount, price=pr, tw_user_id=tweet.user_id, screen_name=tweet.screen_name, direction="buy").save()
                            save_limit_order(symbol=ca.name, token_address=ca.address, amount=amount_to_sell/2, price=pr*2, tw_user_id=tweet.user_id, screen_name=tweet.screen_name,
                                             direction="sell", telegram_id=flower_id)
                        except Exception as e:
                            print(e)
                        await send_message_by_telebot(flower_id ,"bought ca:{0}".format(cas[0]))

async def test(ca):
    amount = 0.01
    pr = tradebot.get_tokenprice_vs_sol(ca)
    token_account = jup.get_token_mint_account(ca)
    sell_token_account_info = await jup.get_token_balance(token_mint_account=token_account)
    print(pr)

    amount_to_sell = sell_token_account_info['balance']['float']

    # await jup.dca(sell_token_address=ca, buy_token_address=SOL_TOKEN_ADDRESS, amount_to_sell=amount_to_sell / 2,
    #               prompt_cycle_frequency=10, max_out_amount=float(float(pr) * 2))

    try:
        # save order in db

        orders(symbol="nameca", token_address="ca.address", stat=1, amount=amount, price=pr, tw_user_id="test",
               screen_name="test").save()
    except Exception as e:
        print(e)

def ca_monitor_bot():
    pertime = 30

    while True:
        try:
            time.sleep(pertime)
            asyncio.run(get_ca_from_tweet(pertime))
        except Exception as e:
            print(e)
            continue

if __name__ == '__main__':
    ca_monitor_bot()
    # asyncio.run(test("4qjGNKLjpqLULH1MEtpi22EG9jwRgfr5NDPybyM6F311"))
    # print(tradebot.get_tokenprice_vs_sol("HctjAgcQTdz5pRBGMsqGGMhZTSFGZfuH4VnvxFjkTFxw"))