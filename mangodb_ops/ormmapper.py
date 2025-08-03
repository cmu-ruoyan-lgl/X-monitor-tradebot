import datetime

from mongoengine import *

# twitter user info
import mangodb_ops.connect
from datetime import datetime
class user_info(DynamicDocument):
    telegram_id = StringField
    wallet_id = StringField
    chat_id = StringField
    monitor_kol_ids = ListField(StringField())
    premium = IntField(default=0)
    user_name = StringField

class wallet(DynamicDocument):
    telegram_id = StringField
    private_key = StringField
    public_key = StringField
    extra_name = StringField
    created_at = DateTimeField(default=datetime.now)
    default = IntField(default=0)

# （1 表示升序，-1 表示降序）, 创建早的数字小
wallet.create_index([('created_at', 1)])


class user_kol_monitor_map(DynamicDocument):
    telegram_id = StringField
    tw_user_id = StringField

class twitter_user(DynamicDocument):
    tw_user_id = StringField
    name = StringField
    screen_name = StringField
    url = StringField
    # if use ListField(StringField) will cause exception
    pinned_tweet_ids = ListField(StringField())
    followers_count = IntField
    lastest_tweet_datetime = StringField
    monitor_status = IntField
    folloer_ids = ListField(StringField())



#tweet info
class tweet(DynamicDocument):
    tw_id = StringField
    created_at_datetime = StringField
    user_id = StringField
    screen_name = StringField
    text = StringField
    reply_count = IntField
    favorite_count = IntField
    view_count = IntField
    retweet_count = IntField

    def get_tw_url(self):
        return "https://x.com/" + self.screen_name+"/status/" + self.tw_id

class latest_tweet(DynamicDocument):
    tw_id = StringField
    tw_user_id = StringField
    screen_name = StringField
    created_at_datetime = StringField

class token_info(DynamicDocument):
    chain = StringField
    symbol = StringField
    name = StringField
    decimals = IntField
    logo = StringField
    address = StringField
    price = DecimalField
    price_1h = DecimalField
    price_24h = DecimalField
    swaps_5m = IntField
    swaps_1h = IntField
    volume_24h = DecimalField
    liquidity = DecimalField
    total_supply = DecimalField
    is_in_token_list = BooleanField
    hot_level = IntField
    is_honeypot = StringField
    renounced = StringField
    top_10_holder_rate = DecimalField
    renounced_mint = StringField
    burn_ratio = DecimalField
    burn_status = StringField
    status = StringField

class orders(DynamicDocument):
    symbol = StringField
    token_address = StringField
    stat = IntField
    amount = FloatField
    price = StringField
    tw_user_id = StringField
    screen_name = StringField
    direction = StringField

class limit_orders(DynamicDocument):
    symbol = StringField
    token_address = StringField
    stat = IntField
    amount = FloatField
    price = StringField
    tw_user_id = StringField
    screen_name = StringField
    direction = StringField
    telegram_id = StringField


class new_pair(DynamicDocument):
    gmgn_id = IntField
    address = StringField
    base_address = StringField
    quote_address = StringField
    liquidity = FloatField
    base_reserve = FloatField
    quote_reserve = FloatField
    initial_liquidity = FloatField
    initial_base_reserve = FloatField
    initial_quote_reserve = FloatField
    creator = StringField
    creation_timestamp = DateTimeField
    quote_reserve_usd = StringField
    burn_ratio = FloatField
    burn_status = StringField
    symbol = StringField
    name = StringField
    decimals = IntField
    total_supply = IntField
    swaps_1h = FloatField
    price = FloatField
    price_1m = FloatField
    price_5m = FloatField
    price_1h = FloatField
    buys_1h = IntField
    sells_1h = IntField
    price_change_percent1m = FloatField
    price_change_percent5m = FloatField
    price_change_percent1h = FloatField
    pool_id = StringField
    is_honeypot = StringField
    renounced = IntField
    renounced_mint = IntField
    social_links = ListField
    market_cap = FloatField
    launchpad = StringField


class new_pair(DynamicDocument):
    gmgn_id = IntField
    address = StringField
    base_address = StringField
    quote_address = StringField
    liquidity = FloatField
    base_reserve = FloatField
    quote_reserve = FloatField
    initial_liquidity = FloatField
    initial_base_reserve = FloatField
    initial_quote_reserve = FloatField
    creator = StringField
    creation_timestamp = DateTimeField
    quote_reserve_usd = StringField
    burn_ratio = FloatField
    burn_status = StringField
    symbol = StringField
    name = StringField
    decimals = IntField
    total_supply = IntField
    swaps_1h = FloatField
    price = FloatField
    price_1m = FloatField
    price_5m = FloatField
    price_1h = FloatField
    buys_1h = IntField
    sells_1h = IntField
    price_change_percent1m = FloatField
    price_change_percent5m = FloatField
    price_change_percent1h = FloatField
    pool_id = StringField
    is_honeypot = StringField
    renounced = IntField
    renounced_mint = IntField
    social_links = ListField
    market_cap = FloatField
    launchpad = StringField
    social_score = FloatField


class new_pair_from_gmgn(object):


    def __init__(self, gmgn_id = None, address = None, base_address = None, quote_address = None, liquidity = None, base_reserve = None,
                         quote_reserve = None, initial_liquidity = None, initial_base_reserve = None , initial_quote_reserve = None,
                         creator = None, creation_timestamp = None, quote_reserve_usd = None, burn_ratio = None, burn_status = None,
                         symbol = None, name = None, decimals = None, total_supply = None,
                         swaps_1h = None, price = None, price_1m = None, price_5m = None,
                         price_1h = None, buys_1h = None, sells_1h = None, price_change_percent1m = None,
                         price_change_percent5m = None, price_change_percent1h = None, pool_id = None,
                         is_honeypot = None, renounced = None, renounced_mint = None,
                         social_links = None, market_cap = None, launchpad = None, holder_count = None, progress = None, score = None) -> None:
        self.gmgn_id = gmgn_id
        self.address = address
        self.base_address = base_address
        self.quote_address = quote_address
        self.liquidity = liquidity
        self.base_reserve = base_reserve
        self.quote_reserve = quote_reserve
        self.initial_liquidity = initial_liquidity
        self.initial_base_reserve = initial_base_reserve
        self.initial_quote_reserve = initial_quote_reserve
        self.creator = creator
        self.creation_timestamp = creation_timestamp
        self.quote_reserve_usd = quote_reserve_usd
        self.burn_ratio = burn_ratio
        self.burn_status = burn_status
        self.symbol = symbol
        self.name = name
        self.decimals = decimals
        self.total_supply = total_supply
        self.swaps_1h = swaps_1h
        self.price = price
        self.price_1m = price_1m
        self.price_5m = price_5m
        self.price_1h = price_1h
        self.buys_1h = buys_1h
        self.sells_1h = sells_1h
        self.price_change_percent1m = price_change_percent1m
        self.price_change_percent5m = price_change_percent5m
        self.price_change_percent1h = price_change_percent1h
        self.pool_id = pool_id
        self.is_honeypot = is_honeypot
        self.renounced = renounced
        self.renounced_mint = renounced_mint
        self.social_links = social_links
        self.market_cap = market_cap
        self.launchpad = launchpad
        self.buy_amount = 0.01

        # for pump
        self.progress = progress
        self.holder_count = holder_count
        self.score = score