import json
import os
import random
import time
from functools import wraps

import twikit
from twikit import Client

from collections import deque

from config import PROXY_URL
import soltradebot.color_constant as color_c
import logging

COOKIES_PATH = '/cookies.json'
client = Client('en-US', proxies=PROXY_URL)
COOKIES = deque()
COOKIES_PROHIBIT = []
current_path = os.path.dirname(__file__)

def check_client_and_retry(retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            current_retries = 0
            while current_retries < retries:
                try:
                    print('call %s():' % func.__name__)
                    reuse_cookies()

                    cookies = get_cookies()
                    if not cookies:
                        print(f"{color_c.RED}can not scrp when has no cookies{color_c.RESET}")
                        return

                    change_cookies(client)
                    return func(*args, **kw)
                except twikit.errors.Unauthorized as te:
                    logging.exception(te)
                    print(f"Error: {te}, Retrying {current_retries}")
                    prohibit_cookies(client.get_cookies())
                except twikit.errors.TwitterException as te:
                    logging.exception(te)
                    print(f"Error: {te}, Retrying {current_retries}")
                    prohibit_cookies(client.get_cookies())
                except KeyError as e:
                    logging.exception(e)
                    break
                except IndexError as e:
                    logging.exception(e)
                    break
                except Exception as e:
                    logging.exception(e)
                    print(f"Error: {e}, Retrying {current_retries}")
                finally:
                    current_retries += 1
        return wrapper
    if type(retries) == int:
        return decorator
    else:
        return decorator(retries)

with open(current_path + COOKIES_PATH, "r", encoding='utf-8') as f:
    lines = f.readlines()
    if lines:
        for line in lines:
            COOKIES.append(json.loads(line))


def login_twitter_for_cookies(username, password, email):
    client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password
    )
    print("login success, save cookies")
    with open(current_path + COOKIES_PATH, 'a+', encoding='utf-8') as f:
        f.write("\n" + json.dumps(client.get_cookies()))


def get_cookies():
    return COOKIES


def set_all_cookies():
    cookies = get_cookies()
    for cook in cookies:
        client.set_cookies(cook)
    print(client.get_cookies())

def get_client():
    cookies = get_cookies()
    if not cookies:
        raise Exception("you must login twitter first")

    client.set_cookies(random.choice(cookies))
    return client

def change_cookies(client:Client):
    cookies = get_cookies()
    if not cookies:
        raise Exception("you must login twitter first")

    if len(cookies) == 1:
        return
    ck = cookies.popleft()
    client.set_cookies(ck)
    cookies.append(ck)


def prohibit_cookies(cookies):
    print(f"{color_c.RED} prohibit the cookies: {cookies} {color_c.RESET}")
    i = 0
    for c in COOKIES:
        i += 1
        if cookies["twid"] == c["twid"]:
            del COOKIES[(i - 1)]
            COOKIES_PROHIBIT.append({int(time.time()): cookies})
            print(COOKIES)
            print(COOKIES_PROHIBIT)
            return
    print("can find the cookies")

def reuse_cookies():
    BLACK_ROOM_TIME = 15 * 60
    now_time = int(time.time())
    i = 0
    for c in COOKIES_PROHIBIT:
        i += 1
        for sincetime, ck in c.items():
            if now_time - sincetime > BLACK_ROOM_TIME:
                COOKIES.append(ck)
                del COOKIES_PROHIBIT[(i-1)]
    if COOKIES_PROHIBIT:
        print(f"prohibit_cookies: {COOKIES_PROHIBIT}")

if __name__ == '__main__':
    # print(time.time())
    # print(time.localtime(time.time()))
    # print(get_cook_from_file('cookies.json'))
    login_twitter_for_cookies("DNr8x00MuW7vN3", "Yl3V1n5Wds","mateogeorgebgd@hotmail.com")