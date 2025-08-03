# tgbotBehavior.py
import asyncio
import functools
from typing import Callable

import base58
from solders.keypair import Keypair
from telegram import Update, Message, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, ConversationHandler, CommandHandler, \
    filters

import config

import soltradebot.color_constant as c
from mangodb_ops.orm_ops import add_kol_follower, check_user_premium, get_wallet_by_user_id, get_wallet_by_private_key, \
    get_wallet_by_pubk, get_wallet_by_id, get_user_by_tele_id, get_kol_by_user_ids, del_kol_follower
from mangodb_ops.ormmapper import user_info, twitter_user, user_kol_monitor_map, wallet
from tw_client import get_client, change_cookies, COOKIES

client = get_client()
print(client.http.client._mounts)
OPEN_PREMIUM_MONITOR_ALTER='''请添加<a href="tg://user?id=6391843369">BTCdachu</a>开通监听服务'''
OPEN_PREMIUM_AUTOBUY_ALTER='''请添加<a href="tg://user?id=6391843369">BTCdachu</a>开通自动买入服务'''

LATEST_HANDLET={}
USER_LATEST_OPS={}
WALLET_MENU, WALLET_MANAGEMENT, SET_DEFAULT_WALLET, SET_WALLET_NAME,SET_WALLET_NAME_ALTER2, ADD_WALLET, DEL_WALLET,CANCEL = range(8)
KOL_MANAGEMENT,ADD_KOL,ADD_KOL_ALTER, DEL_KOL, DEL_KOL_ALTER= range(5)
main_handle_router={}
wallet_handle_router={}
kol_handle_router={}
SET_WALLET_NAME_MAP={}

# 回复固定内容
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 定义一些行为
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    user = user_info.objects(telegram_id=str(user_id)).first()
    if not user:
        print(f"{c.GREEN}New User!{c.RESET}")
        user_info(telegram_id=str(user_id), chat_id=str(chat_id), user_name=str(username)).save()
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='''欢迎使用kol监听机器人！\n 请添加<a href="tg://user?id=6391843369">BTCdachu</a>开通监听服务
                                       ''', parse_mode="html")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"感谢你使用kol监听机器人！")


# 返回 ID

async def add_kol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    your_chat_id = update.effective_chat.id
    # check user if premium
    if not check_user_premium(your_chat_id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=OPEN_PREMIUM_MONITOR_ALTER, parse_mode="html")
        return


    # update.effective_chat.id 就是向机器人发消息的那个用户的 chat id

    message = await context.bot.send_message(chat_id=your_chat_id, text=f'''请输入你要监听的kol名称：''', reply_markup=ForceReply())
    user_id = update.message.from_user.id
    USER_LATEST_OPS.update({user_id: [message.id, ADD_KOL]})
    print(USER_LATEST_OPS)



def add_wallet_db(telegram_id:str, private_key:str, public_key:str):
    user = get_user_by_tele_id(telegram_id)

    print("add wallet to db")
    wallets = get_wallet_by_user_id(user.telegram_id)
    extra_name = public_key[-5:]
    if not wallets:
        w = wallet(telegram_id=telegram_id, private_key=private_key, public_key=public_key, default=1, extra_name=extra_name).save()
        user.private_key = w.private_key
        user.save()
    else:
        w = wallet(telegram_id=telegram_id, private_key=private_key, public_key=public_key, default=0, extra_name=extra_name).save()


def add_kol_db(telegram_id:str, screen_name:str):
    twuser = twitter_user.objects(screen_name=screen_name).first()
    print(twuser)
    if not twuser:
        change_cookies(client)
        print(client.get_cookies())
        user = client.get_user_by_screen_name(screen_name)
        print(
            f'id: {user.id}',
            f'name: {user.name}',
            f'flow: {user.followers_count}',
            f'tweetc: {user.statuses_count}',
            f'screen_name: {user.screen_name}',
            f'pinned_tweet_ids : {user.pinned_tweet_ids}',
            f'url: {user.url}'
        )

        twuser = twitter_user(tw_user_id=user.id, name=user.name, screen_name=user.screen_name, url=user.url,
                     pinned_tweet_ids=user.pinned_tweet_ids, followers_count=user.followers_count,
                     lastest_tweet_datetime="test", monitor_status=1)
        twuser.save()
    monitor_map = user_kol_monitor_map.objects(telegram_id=telegram_id, tw_user_id=twuser.tw_user_id)
    if not monitor_map:
        user_kol_monitor_map(telegram_id=telegram_id, tw_user_id=twuser.tw_user_id).save()
    add_kol_follower(telegram_id, twuser.tw_user_id)

def del_kol_db(telegram_id:str, screen_name:str):
    twuser = twitter_user.objects(screen_name=screen_name).first()
    monitor_map = user_kol_monitor_map.objects(telegram_id=telegram_id, tw_user_id=twuser.tw_user_id)
    if monitor_map:
        monitor_map.delete()
    del_kol_follower(telegram_id, twuser.tw_user_id)

def add_wallet_reply(m:Message):
    pass

def view_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

def del_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

#-------------------------warp------------------------------------------
def return_main(func):
    """
    统计函数耗费时间函数
    """
    @functools.wraps(func)
    async def async_warp(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            print(e)
            return await wallet_management(*args, **kwargs)

    @functools.wraps(func)
    async def sync_warp(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            return await wallet_management(*args, **kwargs)
            print(e)

    # 判断函数是否为异步函数
    if asyncio.iscoroutinefunction(func):
        return async_warp
    else:
        return sync_warp

def check_wallet_warp(func):
    """
    统计函数耗费时间函数
    """
    @functools.wraps(func)
    async def async_warp(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            print(e)
            return await wallet_management(*args, **kwargs)

    @functools.wraps(func)
    async def sync_warp(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            return await wallet_management(*args, **kwargs)
            print(e)

    # 判断函数是否为异步函数
    if asyncio.iscoroutinefunction(func):

        return async_warp
    else:
        return sync_warp


#----------------------------------------

async def wallet_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.get('current_handler')
    user_id = update.message.from_user.id
    # set new state
    return await manage_wallet(user_id, context)

async def manage_wallet(user_id:str, context: ContextTypes.DEFAULT_TYPE)->int:
    global SET_WALLET_NAME_MAP

    if SET_WALLET_NAME_MAP.get(user_id):
        del SET_WALLET_NAME_MAP[user_id]

    if not check_user_premium(str(user_id)):
        await context.bot.send_message(chat_id=user_id,
                                       text=OPEN_PREMIUM_AUTOBUY_ALTER, parse_mode="html")
        ret = await cancel(context)
        return ret
    text = ""
    wallets = get_wallet_by_user_id(str(user_id))
    if wallets:
        for idx, wallet in enumerate(wallets, start=1):
            if wallet.default:
                text += str(idx) + "：{0}📌\n<code>{1}</code>\n".format(wallet.extra_name, wallet.public_key)
            else:
                text += str(idx) + "：{0}\n<code>{1}</code>\n".format(wallet.extra_name, wallet.public_key)

    else:
        "请先绑定钱包"
    keyboard = [
        [InlineKeyboardButton("切换默认钱包", callback_data=str(SET_DEFAULT_WALLET)),
         InlineKeyboardButton("设置钱包名称", callback_data=str(SET_WALLET_NAME))],
        [InlineKeyboardButton("绑定钱包", callback_data=str(ADD_WALLET)),
         InlineKeyboardButton("删除钱包", callback_data=str(DEL_WALLET))],
        [InlineKeyboardButton("返回", callback_data=str(CANCEL))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode="html")
    return WALLET_MENU

def check_private_key(private_key):
    try:
        keypair = Keypair.from_bytes(base58.b58decode(private_key))
        public_key = keypair.pubkey()
        return public_key
    except Exception as e:
        print("Invalid private key:", e)
        return None
async def add_wallet_alter(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    your_chat_id = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    if not check_user_premium(user_id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=OPEN_PREMIUM_AUTOBUY_ALTER, parse_mode="html")
        return wallet_management(update, context)

    # update.effective_chat.id 就是向机器人发消息的那个用户的 chat id
    message = await context.bot.send_message(chat_id=your_chat_id, text=f'''请输入你的钱包私钥（建议使用小钱包）:
⚠️ 请勿导入主钱包或有大额资产的钱包
⚠️ 请勿对外泄露私钥''', reply_markup=ForceReply())
    return ADD_WALLET

async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    message_text = update.message.text
    if get_wallet_by_private_key(str(message_text)):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"已经添加过钱包！")
        return await wallet_management(update, context)
    print("add wallet")
    public_key = check_private_key(message_text)
    if not public_key:
        await context.bot.send_message(chat_id=chat_id, text=f"私钥错误，请重新输入！")
        return ADD_WALLET
    add_wallet_db(str(user_id), str(message_text), str(public_key))
    await context.bot.send_message(chat_id=update.effective_chat.id,text = f"恭喜添加私钥成功！")
    return await wallet_management(update, context)

async def check_user_wallets(update: Update, user_id:str, chat_id, context: ContextTypes.DEFAULT_TYPE):
    wallets = get_wallet_by_user_id(str(user_id))
    if not wallets:
        await wallet_management(update, context)
        await context.bot.send_message(chat_id=chat_id, text=f'''请先导入钱包''',
                                       reply_markup=ForceReply())
        return False
    return wallets

async def set_wallet_name_alter(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    wallets = await check_user_wallets(update, user_id, chat_id, context)
    if not wallets:
        return WALLET_MENU

    # three button one level
    buttons = []
    keyboard = []

    for idx, wallet in enumerate(wallets, start=1):
        buttons.append(InlineKeyboardButton(str(idx), callback_data=str(wallet.id)))
        if idx % 3 == 0:
            keyboard.append(buttons)
            buttons = []

    reply_markup = InlineKeyboardMarkup(keyboard)
    # update.effective_chat.id 就是向机器人发消息的那个用户的 chat id
    message = await context.bot.send_message(chat_id=chat_id, text=f'''请选择希望操作的钱包编号-设置钱包名称''', reply_markup=reply_markup)
    return SET_WALLET_NAME_ALTER2

async def set_wallet_name_alter2(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.effective_chat.id
    wallet_id = update.callback_query.data

    global SET_WALLET_NAME_MAP
    SET_WALLET_NAME_MAP.update({chat_id: wallet_id})
    message = await context.bot.send_message(chat_id=chat_id, text=f'''请输入钱包名称，10个以内的字符，支持汉字，字母，数字组合''', reply_markup=ForceReply())
    return SET_WALLET_NAME

async def set_wallet_name(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    extra_name = update.message.text
    global SET_WALLET_NAME_MAP

    wallet_id = SET_WALLET_NAME_MAP[user_id]



    wallet = get_wallet_by_id(wallet_id)
    wallet.extra_name = extra_name
    wallet.save()
    await wallet_management(update, context)
    return WALLET_MENU

async def set_default_wallet_alter(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    wallets = await check_user_wallets(update, user_id, chat_id, context)
    if not wallets:
        return WALLET_MENU

    # three button one level
    buttons = []
    keyboard = []

    for idx, wallet in enumerate(wallets, start=1):
        buttons.append(InlineKeyboardButton(str(idx), callback_data=str(wallet.id)))
        if idx % 3 == 0:
            keyboard.append(buttons)
            buttons = []

    reply_markup = InlineKeyboardMarkup(keyboard)
    # update.effective_chat.id 就是向机器人发消息的那个用户的 chat id
    message = await context.bot.send_message(chat_id=chat_id, text=f'''请选择希望操作的钱包编号-设置默认钱包''', reply_markup=reply_markup)
    return SET_DEFAULT_WALLET

async def set_default_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.callback_query.from_user.id
    wallet_id = str(update.callback_query.data)

    user = get_user_by_tele_id(chat_id)
    wallet_default = get_wallet_by_id(user.wallet_id)

    wallet = get_wallet_by_id(wallet_id)

    if str(wallet_default.id) != wallet_id:
        user.wallet_id = wallet_id
        user.save()

        wallet_default.default = 0
        wallet_default.save()

        wallet.default = 1
        wallet.save()

    await manage_wallet(chat_id, context)
    return WALLET_MENU

async def del_wallet_alter(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    wallets = await check_user_wallets(update, user_id, chat_id, context)
    if not wallets:
        return WALLET_MENU

    # three button one level
    buttons = []
    keyboard = []

    for idx, wallet in enumerate(wallets, start=1):
        buttons.append(InlineKeyboardButton(str(idx), callback_data=str(wallet.id)))
        if idx % 3 == 0:
            keyboard.append(buttons)
            buttons = []

    reply_markup = InlineKeyboardMarkup(keyboard)
    # update.effective_chat.id 就是向机器人发消息的那个用户的 chat id
    message = await context.bot.send_message(chat_id=chat_id, text=f'''请选择希望操作的钱包编号-设置默认钱包''', reply_markup=reply_markup)
    return SET_DEFAULT_WALLET

async def set_default_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.callback_query.from_user.id
    wallet_id = str(update.callback_query.data)

    user = get_user_by_tele_id(chat_id)
    wallet_default = get_wallet_by_id(user.wallet_id)

    wallet = get_wallet_by_id(wallet_id)

    if str(wallet_default.id) != wallet_id:
        user.wallet_id = wallet_id
        user.save()

        wallet_default.default = 0
        wallet_default.save()

        wallet.default = 1
        wallet.save()

    await manage_wallet(chat_id, context)
    return WALLET_MENU

async def cancelConversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("end conversation")
    return ConversationHandler.END
async def cancel(context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END
async def wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    callback_data = Update.callback_query

    func = wallet_handle_router.get(callback_data)
    if not func:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"未找到命令，请重新输入！")
        return WALLET_MENU

    next_step = await func(update, context)
    return next_step

wallet_handle_router.update({str(ADD_WALLET): add_wallet_alter})
wallet_handle_router.update({str(SET_WALLET_NAME): set_wallet_name_alter})
wallet_handle_router.update({str(SET_WALLET_NAME_ALTER2): set_wallet_name_alter2})
default_status = [
        CallbackQueryHandler(add_wallet_alter, pattern="^" + str(ADD_WALLET) + "$"),
        CallbackQueryHandler(wallet_menu, pattern='^{0}$'.format(DEL_WALLET)),
        CallbackQueryHandler(set_wallet_name_alter, pattern="^" + str(SET_WALLET_NAME) + "$"),
        CallbackQueryHandler(set_default_wallet_alter, pattern="^" + str(SET_DEFAULT_WALLET) + "$"),
        CallbackQueryHandler(wallet_menu, pattern='^{0}$'.format(DEL_WALLET)),
        CallbackQueryHandler(cancel, pattern="^" + str(CANCEL) + "$")
]
add_wallet_status =  [
        CallbackQueryHandler(add_wallet_alter, pattern="^" + str(ADD_WALLET) + "$"),
        CallbackQueryHandler(wallet_menu, pattern='^{0}$'.format(DEL_WALLET)),
        CallbackQueryHandler(set_wallet_name_alter, pattern="^" + str(SET_WALLET_NAME) + "$"),
        CallbackQueryHandler(set_default_wallet_alter, pattern="^" + str(SET_DEFAULT_WALLET) + "$"),
        CallbackQueryHandler(wallet_menu, pattern='^{0}$'.format(DEL_WALLET)),
        CallbackQueryHandler(wallet_menu, pattern='^{0}$'.format(CANCEL))
]
states_functions = {
    WALLET_MENU: default_status,
    ADD_WALLET: add_wallet_status,
    SET_WALLET_NAME_ALTER2: [
        CallbackQueryHandler(set_wallet_name_alter2)
    ],
    SET_DEFAULT_WALLET: [
        CallbackQueryHandler(set_default_wallet)
    ],
    SET_WALLET_NAME: [
        MessageHandler(filters.TEXT & ~filters.COMMAND, set_wallet_name)
    ],
    DEL_WALLET: [
        CallbackQueryHandler(filters.TEXT & ~filters.COMMAND, del_wallet)
    ]
}
wallet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("wallet_management", wallet_management)],
    states=states_functions,
    fallbacks=[MessageHandler(filters.COMMAND, cancelConversation)]
)

async def kol_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    return await manage_kol(user_id, context)

async def manage_kol(user_id:str, context: ContextTypes.DEFAULT_TYPE)->int:


    if not check_user_premium(str(user_id)):
        await context.bot.send_message(chat_id=user_id,
                                       text=OPEN_PREMIUM_AUTOBUY_ALTER, parse_mode="html")
        ret = await cancel(context)
        return ret


    text = ""
    user = get_user_by_tele_id(user_id)
    kols = get_kol_by_user_ids(user.monitor_kol_ids)
    if kols:
        for idx, kol in enumerate(kols, start=1):
            text += str(idx) + ":<code>{0}</code>\n".format(kol.screen_name)
    else:
        text = "请先添加kol"

    keyboard = [
        [InlineKeyboardButton("监控kol", callback_data=str(ADD_KOL_ALTER)),
         InlineKeyboardButton("取消监控kol", callback_data=str(DEL_KOL_ALTER))],
        [InlineKeyboardButton("返回", callback_data=str(CANCEL))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode="html")
    return KOL_MANAGEMENT

async def add_kol_alter(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    user_id = update.callback_query.from_user.id

    await context.bot.send_message(chat_id=user_id, text=f'''请输入你要监听的kol名称：''', reply_markup=ForceReply())
    return ADD_KOL

async def add_kol(update: Update, context: ContextTypes.DEFAULT_TYPE) ->int:
    chat_id = update.message.id
    user_id = update.message.from_user.id
    screen_name = update.message.text
    add_kol_db(telegram_id=user_id, screen_name=screen_name)
    await manage_kol(user_id, context)
    return KOL_MANAGEMENT


async def del_kol_alter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.callback_query.from_user.id

    await context.bot.send_message(chat_id=user_id, text=f'''请输入你要取消监控的kol名称：''', reply_markup=ForceReply())
    return DEL_KOL


async def del_kol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.id
    user_id = update.message.from_user.id
    screen_name = update.message.text
    del_kol_db(telegram_id=user_id, screen_name=screen_name)
    await manage_kol(user_id, context)
    return KOL_MANAGEMENT

kol_states_functions = {
    KOL_MANAGEMENT: [
        CallbackQueryHandler(add_kol_alter, pattern="^" + str(ADD_KOL_ALTER) + "$"),
        CallbackQueryHandler(del_kol_alter, pattern="^" + str(DEL_KOL_ALTER) + "$")
    ],
    ADD_KOL: [
        MessageHandler(filters.TEXT & ~filters.COMMAND, add_kol)
    ],
    DEL_KOL: [
        MessageHandler(filters.TEXT & ~filters.COMMAND, del_kol)
    ]
}
kol_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("kol_management", kol_management)],
    states=kol_states_functions,
    fallbacks=[MessageHandler(filters.COMMAND, cancelConversation)]
)

if __name__ == '__main__':
    test = user_info.objects(telegram_id="6391843369").first()
    if not test:
        print("yes")