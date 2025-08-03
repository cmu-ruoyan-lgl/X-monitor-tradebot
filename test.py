import time

from kol_tw_monitor_bot import check_client_and_retry
from tw_client import login_twitter_for_cookies, get_cookies, set_all_cookies, prohibit_cookies, reuse_cookies, \
    get_client, change_cookies

client = get_client()

@check_client_and_retry
def test11():
    print("test111")
# Initialize client
if __name__ == '__main__':
    # print(time.time())
    # print(time.localtime(time.time()))
    # print(get_cook_from_file('cookies.json'))
    #login_twitter_for_cookies("sof1dBsdlsa1xh", "twLR7M6K3o","elijahtctucker@hotmail.com")
    # set_all_cookies()
    # prohibit_cookies({"guest_id_marketing": "v1%3A171634694922368599", "guest_id_ads": "v1%3A171634694922368599", "personalization_id": "\"v1_wESDvplhUDCSBplCismDVw==\"", "guest_id": "v1%3A171634694922368599", "att": "1-pTRfXzRK7KEuAzvHTmTPoCsAVPXDSXc52pTf4KiO", "kdt": "8HIWkzQEi3gH9qYkryCwX9gN8rKpQAWdvwFvAvIT", "twid": "\"u=4618557503\"", "ct0": "7ee5f4219d581f61aabd890a8c707f7e", "auth_token": "80e28b7f6f2d48e86869db10b8720a710690bb22"})
    # time.sleep(12)
    # reuse_cookies()
    #test11()
    # change_cookies(client)
    # for tw in client.get_user_tweets(user_id="448953935", tweet_type="Tweets", count=10):
    #     print(tw.created_at)
    # pr = 1.54439846e-06
    # num_value = '{:.20f}'.format(pr)
    #
    # print(num_value)
    # print(float(pr))
    # x = float(pr) - 0.000001
    # print(x)
    # test = {"1":"2"}

    # print(test.get("2"))
    print(int(61/60))
    print((1, 0.1)[1 > 0.1])