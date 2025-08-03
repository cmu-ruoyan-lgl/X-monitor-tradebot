import asyncio

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.request import HTTPXRequest

from config import PROXY_URL
from mangodb_ops.ormmapper import tweet, twitter_user
import mangodb_ops.connect
from telegrambot.config import bot_token
from utils.warp_utils import catch_error

TOKEN="6804374758:AAHiNUBmwmmPlLEA5yHymPfEI8v4EX6_FNc"
HTTP_URL="https://api.telegram.org/bot{0}/sendMessage".format(TOKEN)
CHAT_ID=6391843369
TOKEN2="7405870966:AAFTEo8scVJE5CTOH9O6rp9pVNbOp1K7nkk"


trequest = HTTPXRequest(proxy_url=PROXY_URL,connection_pool_size=20, connect_timeout=30, read_timeout=30, write_timeout=30)
bot = telegram.Bot(token=bot_token, request=trequest)
async def send_message_by_telebot(chat_id, message):
    await bot.send_message(chat_id=chat_id,  text=message)

async def send_tw_by_telebot(chat_id, tw: tweet):
    # print('''
    #     *KOL:{0}*
    #     >{1}
    #     ||{2}||
    # '''.format(tw.screen_name, tw.text, tw.get_tw_url()))
    re = await bot.send_message(chat_id=chat_id, text='''
<b>KOL:{0} 发推了</b>
<blockquote color="#f6ebc1">{1}</blockquote>
        
        
原文链接：{2}
    '''.format(tw.screen_name, tw.text, tw.get_tw_url()), parse_mode="HTML", disable_web_page_preview=True)

@catch_error
async def send_ca_by_telebot(chat_id, ca:str, tw:tweet):

        # 创建内联按钮
    button_text = "点击购买"
    button_url = "https://t.me/pepeboost_sol15_bot?start=" + ca
    inline_button = InlineKeyboardButton(text=button_text, url=button_url, switch_inline_query=ca)

    # 将按钮添加到内联键盘中
    inline_keyboard = [[inline_button]]
    inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await bot.send_message(chat_id=chat_id, text='''
<b>NEW CA:<code>{0}</code></b>

喊单kol：{1}
推文链接：{2}
    '''.format(ca, tw.screen_name, tw.get_tw_url()), parse_mode="html", reply_markup=inline_reply_markup,disable_web_page_preview=True )


if __name__ == '__main__':
    t = tweet.objects(tw_id="1793988373096603876").first()
    print(t)
    #asyncio.run(send_tw_by_telebot(6391843369, t))
    asyncio.run(send_ca_by_telebot("1496126936", "test", t))