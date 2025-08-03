from bson import ObjectId

from mangodb_ops.ormmapper import twitter_user, tweet, token_info, latest_tweet, limit_orders, user_kol_monitor_map, \
    user_info, wallet

import mangodb_ops.connect
def get_twitter_user(USER_ID):
    return twitter_user.objects(tw_user_id=USER_ID).first()

def get_twitter_user_by_user(telegram_id:str):
    return user_info.objects(telegram_id=str(telegram_id)).first()

def insert_twitter_user(twitter_user):
    twitter_user.objects.save()

def get_all_premium_users():
    return user_info.objects(premium=1)

def get_latest_tweet_by_userid(USER_ID):
    return latest_tweet.objects(tw_user_id=USER_ID).order_by('created_at_datetime').first()

def get_all_twitter_user_monitor():
    return twitter_user.objects(monitor_status=1)

def get_tweet_since_time(data):
    return tweet.objects(created_at_datetime__gt=data)

def get_ca_by_address_db(address):
    return token_info.objects(address=address).first()

def update_latest_tweet_db(tweet):
    tweet_old = latest_tweet.objects(tw_user_id=tweet.tw_user_id)
    if not tweet_old:
        tweet.save()
        return

    tweet_old = latest_tweet.objects.get(tw_user_id=tweet.tw_user_id)
    tweet_old.tw_id = tweet.tw_id
    tweet_old.created_at_datetime = tweet.created_at_datetime
    tweet_old.save()

def save_limit_order(symbol, token_address, amount, price, tw_user_id, screen_name, direction, telegram_id):
    limit_orders(symbol=symbol, token_address=token_address, amount=amount, price=price,
                 tw_user_id=tw_user_id, screen_name=screen_name,direction=direction, telegram_id=telegram_id, stat=1).save()


def get_user_kol_map():
    return user_kol_monitor_map.objects()

def get_user():
    return user_info.objects()

def check_user_premium(user_id:str):
    user = user_info.objects(telegram_id=str(user_id)).first()
    if not user:
        return False

    return user.premium
def add_kol_follower(follwer_id:str, kol_id:str):
    follwer_id = str(follwer_id)
    kol_id = str(kol_id)
    user = user_info.objects.get(telegram_id=str(follwer_id))
    kol = twitter_user.objects.get(tw_user_id=str(kol_id))

    if kol_id not in user.monitor_kol_ids:
        user.monitor_kol_ids.append(kol_id)
        user.save()

    if follwer_id not in kol.folloer_ids:
        kol.folloer_ids.append(follwer_id)
        kol.save()

def del_kol_follower(follwer_id:str, kol_id:str):
    user = user_info.objects.get(telegram_id=str(follwer_id))
    kol = twitter_user.objects.get(tw_user_id=kol_id)

    if kol_id in user.monitor_kol_ids:
        user.monitor_kol_ids.remove(kol_id)
        user.save()

    if follwer_id in kol.folloer_ids:
        if len(kol.folloer_ids) == 1:
            kol.delete()
        else:
            kol.folloer_ids.remove(follwer_id)
            kol.save()

def get_all_wallets():
    return wallet.objects(default=1)

def get_wallet_by_user_id(user_id:str):
    return wallet.objects(telegram_id=str(user_id)).order_by('created_at')

def get_kol_by_user_ids(tw_user_ids:list):
    return twitter_user.objects(tw_user_id__in=tw_user_ids).order_by('followers_count')


def get_wallet_by_private_key(private_key:str):
    return wallet.objects(private_key= ObjectId(private_key)).first()

def get_wallet_by_pubk(pubk:str):
    return wallet.objects(public_key= pubk).first()

def get_wallet_by_id(id:str):
    return wallet.objects(id=id).first()

def get_user_by_tele_id(tele_id:str):
    return user_info.objects(telegram_id= str(tele_id)).first()


if __name__ == '__main__':
    # add_kol_follower("6391843369", "1675699945893154816")
    print(check_user_premium(6391843369))

