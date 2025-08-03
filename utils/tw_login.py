import json
import os
import random
import time

from twikit import Client

from collections import deque

from mangodb_ops.orm_ops import get_twitter_user_by_user

COOKIES_PATH = '/cookies.json'
client = Client('en-US', proxies="http://127.0.0.1:57128")

p_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
print(p_path)
COOKIES_TWIDS = []
COOKIES = []


ACCOUNT_PATH="tw_account"

with open(p_path + COOKIES_PATH, "r", encoding='utf-8') as f:
    lines = f.readlines()
    if lines:
        for line in lines:
            COOKIES_TWIDS.append(json.loads(line)['twid'])
            COOKIES.append(json.loads(line))
def login_twitter_for_cookies():
    accounts = []

    with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if lines:
            for line in lines:
                s = line.split("----")
                print(s)
                accounts.append([s[0], s[1], s[2], s[4]])
    for account in accounts:
        try:
            print(account)
            client.http.client.cookies.clear()
            client.login(
                auth_info_1=account[0],
                auth_info_2=account[2],
                password=account[1],
                fatoken=account[3]
            )
            print("login success, save cookies")
            print(client.get_cookies())
            if client.get_cookies()["twid"] in COOKIES_TWIDS:
                print("already login")
            else:
                with open(p_path + COOKIES_PATH, 'a+', encoding='utf-8') as f:
                    f.write("\n" + json.dumps(client.get_cookies()))
                COOKIES_TWIDS.append(client.get_cookies()["twid"])
            time.sleep(30)
        except Exception as e:
            print(e)
            continue

def follow_kol(kol_id:str):
    for ck in COOKIES_TWIDS:
        client.set_cookies(ck)
        client.follow_user(kol_id)

def follow_kol_from_db():
    while True:
        try:
            kols = get_twitter_user_by_user("6391843369").monitor_kol_ids
            for ck in COOKIES:
                print(ck["twid"])
                client.set_cookies(ck)
                for kol in kols:
                    rsp = client.follow_user(kol)
                    print(rsp)
                    time.sleep(300)
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    login_twitter_for_cookies()
    # follow_kol_from_db()