import datetime
import json
import os
import random
import time
import mangodb_ops.connect

from twikit import Client, Tweet

from mangodb_ops.orm_ops import get_twitter_user
from mangodb_ops.ormmapper import twitter_user, tweet
from tw_client import get_client

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

def callback(tweet: Tweet) -> None:
    print(f'New tweet posted : {tweet.text}')

def get_latest_tweet(USER_ID, TYPE) -> Tweet:
    tweets = client.get_user_tweets(USER_ID, TYPE)
    if tweets:
        return tweets[0]
    return None

def get_latest_reply_tweet(USER_ID) -> Tweet:
    tweets = client.get_user_tweets(USER_ID, 'Replies')
    if tweets:
        return tweets[0]
    return None

def get_latest_tweets_tweet(USER_ID) -> Tweet:
    tweets = client.get_user_tweets(USER_ID, 'Tweets')
    if tweets:
        return tweets[0]
    return None

def get_latest_Likes_tweet(USER_ID) -> Tweet:
    tweets = client.get_user_tweets(USER_ID, 'Likes')
    if tweets:
        return tweets[0]
    return None


def get_new_tweets(USER_ID:str):
    CHECK_INTERVAL = 60 * 5
    before_tweet = get_lastest_tweet_byuserid(USER_ID)

    while True:
        need_insert = False
        time.sleep(CHECK_INTERVAL)
        for tweet_type in ['Tweets', 'Replies', 'Likes']:
            randomtime = random.randint(1, 60)
            time.sleep(randomtime)
            latest_tweet = get_latest_tweet(USER_ID, tweet_type)
            if latest_tweet is None:
                continue
            if before_tweet is None:
                before_tweet = latest_tweet
                need_insert = True
            if (
                before_tweet != latest_tweet and
                transfer_time(before_tweet.created_at) < transfer_time(latest_tweet.created_at)
            ):
                before_tweet = latest_tweet
                need_insert = True

            if need_insert:
                callable(latest_tweet)
                tweet(tw_id=before_tweet.id, created_at_datetime = transfer_time(before_tweet.created_at), user_id=USER_ID, text=before_tweet.text, reply_count=before_tweet.reply_count,
                      favorite_count=before_tweet.favorite_count, view_count=before_tweet.view_count, retweet_count=before_tweet.view_count).save()

def transfer_time(time_str):
    dt_obj = datetime.datetime.strptime(time_str, '%a %b %d %H:%M:%S %z %Y')
    timeArray = dt_obj.astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S')
    return  int(time.mktime(time.strptime(timeArray, "%Y-%m-%d %H:%M:%S")))

if __name__ == '__main__':
    SCAN_NAME = "gritx426"
    user = client.get_user_by_screen_name(SCAN_NAME)
    print(
        f'id: {user.id}',
        f'name: {user.name}',
        f'flow: {user.followers_count}',
        f'tweetc: {user.statuses_count}',
        f'screen_name: {user.screen_name}',
        f'pinned_tweet_ids : {user.pinned_tweet_ids}',
        f'url: {user.url}'
    )
    if not get_twitter_user(user.id):
        print("add new user to monitor")

        twitter_user(tw_user_id=user.id, name=user.name, screen_name=user.screen_name, url=user.url, pinned_tweet_ids=user.pinned_tweet_ids, followers_count=user.followers_count, lastest_tweet_datetime="test", monitor_status=1).save()

    #get_new_tweets(user.id)