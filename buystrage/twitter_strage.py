import time

import twikit

from tw_client import get_client, check_client_and_retry
import soltradebot.color_constant as color_c
from utils.time_utils import transfer_time

client = get_client()
KOL_BACK_LIST = {"GetXTrending", "sxfclzlkw", "Sol_Launch", "snipegurusolvol", "niickdmnd"}
UTCTIME_2020 = 1591325570

class coin_score(object):
    def __init__(self) -> None:
        super().__init__()
        self.ca_tw_follower_score = 0
        self.same_follower_score = 0
        self.creator_follower_score = 0
        self.ca_tw_view_score = 0

    def get_coin_score(self):
        return self.ca_tw_view_score + self.same_follower_score + self.ca_tw_follower_score + self.creator_follower_score


# 1.get score of new ca
@check_client_and_retry(5)
def get_community_popularity_for_newpair(query:str, twitter_name=None):
    tws = client.search_tweet(query=query, product="Top")

    user = client.get_user_by_screen_name(twitter_name)

    cs = coin_score()
    cs.ca_tw_follower_score = get_tw_flower_score(tws)


    true_kol = False
    if user:
        tws_from_user = client.get_user_tweets(user_id=user.id, tweet_type="Tweets", count=20)
        for tw in tws_from_user:
            if query in tw.text:
                true_kol = True
                break
    if true_kol:
        cs.same_follower_score = get_same_flowers_score_for_pump_by_twuser(user)
        cs.creator_follower_score = get_flowers_score(query, user)
    cs.ca_tw_view_score = get_view_score(tws)

    print(f"{color_c.GREEN}[{query}] score:\n"
          f"ca tw follower score:{cs.ca_tw_follower_score} \n"
          f"ca tw view score:{cs.ca_tw_view_score}\n"
          f"creator same followers score: {cs.same_follower_score}\n"
          f"creator follower score:{cs.creator_follower_score}\n {color_c.RESET}")
    return cs.get_coin_score()


def get_tw_flower_score(tws:[]):
    score = 0
    kol_count = 0
    kols = []
    for tw in tws:
        tw_flowers = tw.user.followers_count
        sn = tw.user.screen_name

        if tw.user.id in kols:
            continue
        if sn in KOL_BACK_LIST:
            continue
        elif tw_flowers > 10000:
            score += (tw_flowers/10000) * 30
            kol_count += 1
        elif tw_flowers > 1000:
            score += 20
            kol_count += 1
        elif tw_flowers > 500:
            score += 10
            kol_count += 1

        kols.append(tw.user.id)
    return score

def get_same_follower_score_from_tw(tws:[]):
    score = 0
    kol_count = 0
    kols = []
    for tw in tws:
        id = tw.user.id

        if id in kols:
            continue
        score += get_same_flowers_score_by_id(id)

        kols.append(id)
    return score

def get_same_flowers_score_by_id(id:str):
    same_flowers = client.get_user_followers_you_know(id)
    return 5 * len(same_flowers)

def get_same_flowers_score_by_screen_name(user:twikit.User):
    same_flowers = client.get_user_followers_you_know(user.id)

    return 5 * len(same_flowers)

def get_flowers_score(query:str=None, user:twikit.User = None):

    score = 0

    if user.followers_count > 10000:
        score += (user.followers_count / 10000) * 30
    elif user.followers_count > 1000:
        score += (user.followers_count / 1000) * 10
    elif user.followers_count > 500:
        score += 10
    return score

def get_view_score(tws:[]):
    score = 0
    for tw in tws:
        view_count = int(tw.view_count)

        score += ((view_count / 100) * 0.5)
    return score


@check_client_and_retry(5)
def get_community_popularity_for_newpump(query:str, twitter_name=None):
    tws = client.search_tweet(query=query, product="Top")
    score = 0
    score += get_tw_flower_score(tws)
    score += get_view_score(tws)
    true_kol = False
    if twitter_name:
        user = client.get_user_by_screen_name(twitter_name)
        if user:
            tws_from_user = client.get_user_tweets(user_id=user.id, tweet_type="Tweets", count=20)
            for tw in tws_from_user:
                if query in tw.text:
                    true_kol = True
                    break
    if true_kol:
        score += get_same_flowers_score_for_pump_by_twuser(user)
        score += get_flowers_score(query, user)
    return score


def get_same_flowers_score_for_pump_by_twuser(user:twikit.User):
    same_flowers = client.get_user_followers_you_know(user.id)

    return 15 * len(same_flowers)

def get_tw_view_by_tw_id(tw_id):
    tw_view_count = client.get_tweet_by_id(tweet_id=tw_id)

    return tw_view_count

def get_tw_by_filter_text_twid(tw_user_id, text:str) -> twikit.Tweet:
    if tw_user_id:
        tws_from_user = client.get_user_tweets(user_id=tw_user_id, tweet_type="Tweets", count=20)
        latest_time = int(time.time())
        _tw = None
        for tw in tws_from_user:
            if text in tw.text:
                c_t = transfer_time(tw.created_at)
                if c_t < latest_time:
                    _tw = tw
                    latest_time = c_t
    return _tw

def get_tw_id_from_twitter_name(twitter_name):
    try:
        user = client.get_user_by_screen_name(twitter_name)
        return user.id
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    # tws = get_community_popularity_for_newpair("4Cnk9EPnW5ixfLZatCPJjDB1PUtcRpVVgTQukm9epump", "DaddyTateCTO")
    #
    # print(tws)
    # user_id = get_tw_id_from_twitter_name("SpideySOLANA_")
    # tw = get_tw_by_filter_text_twid(user_id, "3YG6591aJ1KzyYDGXzSsYQBzByTmtkyfUHDYjUaqpump")
    # print(tw.text)

    tw = client.get_tweet_by_id("1804046403422859533")
    print(tw.text)
    # tws = get_community_popularity_for_newpump("2THAACwAdrcQsXat8L3xsY5e9uH4PTeJKCWNcatqpump", "Bitchespepe")
    # print(tws)
    # user = client.get_user_by_screen_name("BryceHall")
    # print(transfer_time(user.created_at))

