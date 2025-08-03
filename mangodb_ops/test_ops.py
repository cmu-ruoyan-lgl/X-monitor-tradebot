from mangodb_ops.orm_ops import  get_tweet_since_time, get_all_twitter_user_monitor, \
    update_latest_tweet_db
from mangodb_ops.ormmapper import twitter_user, latest_tweet, orders
import mangodb_ops.connect
if __name__ == '__main__':
    #print(get_lastest_tweet_byuserid('1675699945893154816') is None)
    #print(get_tweet_since_time(171626753)[0].tw_id)
    #print(get_all_twitter_user_monitor())
    #update_latest_tweet_db(latest_tweet(tw_id="test", tw_user_id='test',screen_name="test",created_at_datetime="test"))
    # test = latest_tweet.objects(tw_user_id="1385952907233841160")
    # if not test:
    #     print("test")
    o = orders.objects()
    for o1 in o:

        print(o1.price)
        print(type(o1.price))
        if 1.19670287e-07 < o1.price:
            print("yes")