import os

from telegram import Update, BotCommand  # 获取消息队列的
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
import config
# 从 tgbotBehavior.py 导入定义机器人动作的函数
from tgbotBehavior import start, add_kol, add_wallet, wallet_menu, wallet_conv_handler, wallet_management, \
    kol_conv_handler, kol_management
import mangodb_ops.connect
#add menus
command_info = [
    BotCommand("start", "start bot"),
    BotCommand("wallet_management", "add wallet to buy coin auto"),
    BotCommand("kol_management", "add kol to monitor")
]

async def post_init(application: Application) -> None:
    bot = application.bot
    await bot.set_my_commands(commands=command_info)

def create_and_run_bot():
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    proxy_url = 'http://127.0.0.1:51204'
    application = ApplicationBuilder().token(config.bot_token).proxy_url(proxy_url).get_updates_proxy_url(
        proxy_url).post_init(post_init).build()

    # understand different group
    application.add_handler(wallet_conv_handler, 2)
    application.add_handler(kol_conv_handler, 3)
    application.add_handler(CommandHandler("start", start), 1)
    # application.add_handler(CommandHandler("wallet_management", wallet_management), 1)
    # application.add_handler(CommandHandler("kol_management", kol_management), 1)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    create_and_run_bot()