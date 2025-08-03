import asyncio
import json
import os
import random
import time
from functools import wraps

from twikit import Tweet, client, Client

from mangodb_ops.orm_ops import get_all_twitter_user_monitor, get_latest_tweet_by_userid, update_latest_tweet_db, \
    get_user_kol_map, get_user, get_all_premium_users
from mangodb_ops.ormmapper import tweet, latest_tweet
from telegrambot.telegram_bot_alter import send_message_by_telebot, send_tw_by_telebot
from tw_client import get_client, change_cookies, get_cookies, reuse_cookies, prohibit_cookies, check_client_and_retry
from utils.time_utils import transfer_time
import mangodb_ops.connect
import soltradebot.color_constant as c

# Initialize client
client = get_client()


def get_cook_from_file(path:str):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            cook = f.read()
            return cook
    return None

def login():
    cookie = get_cook_from_file('cookies.json')
    if cookie:
        print(cookie)
        client.set_cookies(json.loads(cookie))
        return

    # USERNAME = '@BTCdachu'
    # EMAIL = 'btcdachu@gamil.com'
    # PASSWORD = '@MootsBtc1234'

    USERNAME = '@ddjdjdjjssbshs'
    EMAIL = 'jena94botsfordxky@outlook.com'
    PASSWORD = 'O7ur6EuYsK9'

    client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD
    )

    client.save_cookies('cookies.json')

@check_client_and_retry()
def get_latest_tweet(USER_ID, TYPE) -> Tweet:
    tweets = client.get_user_tweets(user_id=USER_ID, tweet_type=TYPE, count=10)
    if tweets:
        return tweets
    return None



def callback(tweet: Tweet) -> None:
    print(f'New tweet posted : {tweet.text}')

async def monitor_kol_tw():
    # get all kol from db
    kols = get_all_twitter_user_monitor()
    users = get_all_premium_users()
    user_chat_map = {}
    for user in users:
        user_chat_map.update({user.telegram_id:user.chat_id})
    print(user_chat_map)
    print(kols)
    while True:
        CHECK_INTERVAL = 60
        time.sleep(CHECK_INTERVAL)
        for twitter_user in kols:
            print('''
                monitor kol_id: {0}
                kol_screen_name: {1}
            '''.format(twitter_user.tw_user_id, twitter_user.screen_name))

            # randomtime = random.randint(1, 60)
            # time.sleep(randomtime)


            need_insert = False
            # get lastest tweet from db
            TWITTER_USER_ID = twitter_user.tw_user_id
            before_tweet = get_latest_tweet_by_userid(TWITTER_USER_ID)
            print(before_tweet)

            cur_time = int(time.time())
            #for tweet_type in ['Tweets', 'Replies', 'Likes']:
            for tweet_type in ['Tweets']:
                latest_tweet_from_website = get_latest_tweet(TWITTER_USER_ID, tweet_type)
                if latest_tweet_from_website is None:
                    continue
                if before_tweet is None:
                    need_insert = True
                else:
                    if (
                        # if latest tweet newthan db, add to db
                        before_tweet.created_at_datetime < transfer_time(latest_tweet_from_website[0].created_at)
                    ):
                        need_insert = True
                if need_insert:
                    for tw in latest_tweet_from_website:
                        if not before_tweet or before_tweet.created_at_datetime < transfer_time(tw.created_at):
                            callable(latest_tweet_from_website)
                            t = tweet(tw_id=tw.id, created_at_datetime=transfer_time(tw.created_at),
                                  user_id=TWITTER_USER_ID, screen_name = twitter_user.screen_name, text=tw.text, reply_count=tw.reply_count,
                                  favorite_count=tw.favorite_count, view_count=tw.view_count,
                                  retweet_count=tw.view_count).save()

                            # if only the 3 minute send alter to follers
                            if transfer_time(tw.created_at) < cur_time - 300:
                                continue
                            # alter telegram
                            for foller_id in twitter_user.folloer_ids:
                                if user_chat_map.get(foller_id):
                                    await send_tw_by_telebot(user_chat_map[foller_id] ,t)
                    print("update latest tweet")
                    update_latest_tweet_db(latest_tweet(tw_id=latest_tweet_from_website[0].id, tw_user_id=twitter_user.tw_user_id,
                                                        screen_name=twitter_user.screen_name,
                                                        created_at_datetime=transfer_time(latest_tweet_from_website[0].created_at)))

if __name__ == '__main__':
    while True:
        try:
            asyncio.run(monitor_kol_tw())
        except Exception as e:
            print(e)
            time.sleep(60)
            continue
