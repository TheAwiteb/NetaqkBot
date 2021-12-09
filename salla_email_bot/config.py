"""
سوف يتم حفظ المتغيرات الاساسية في هذا الملف
"""
from os import environ
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
)

load_dotenv()

# التوكن الخاص بالبوت
# يمكن جلب التوكن الخاص بالبوت من
# @ https://t.me/botfather
TOKEN = (
    ""  # ضع التوكن هنا
    or environ.get("TELEGRAM_BOT_TOKEN")  # او عرفه كمتغير في البيئة
    or input(
        "Enter your bot token (Get from @ https://t.me/botfather): "
    )  # او ادخله عند طلبه منك
)

# البوت
BOT: TeleBot = TeleBot(TOKEN)

# الرابط الخاص بالتيليجرام
telegram_url = "https://t.me/"

# اسم البوت
bot_name = BOT.get_me().first_name

# اسم المستخدم الخاص بالبوت
bot_username = BOT.get_me().username


# الاوامر الخاصة بالبوت
COMMANDS = {
    # الاوامر باللغة العربية
    "ar": {
        BotCommandScopeDefault: [
            BotCommand("about", "عن البوت."),
        ],
        # الاوامر الخاصة بالدردشات الخاصة ( بين الوت والمستخدم)
        BotCommandScopeAllPrivateChats: [
            BotCommand("about", "عن البوت."),
            BotCommand("help", "رسالة المساعدة."),
            BotCommand("start", "رسالة البداية."),
            BotCommand("login", "تسجيل الدخول الى حسابك."),
            BotCommand("logout", "تسجيل الخروج من حسابك."),
        ],
    },
    # الاوامر باللغات الاخرى
    "-": {
        BotCommandScopeDefault: [
            BotCommand("about", "About the bot."),
        ],
        # الاوامر الخاصة بالدردشات الخاصة ( بين الوت والمستخدم)
        BotCommandScopeAllPrivateChats: [
            BotCommand("about", "About the bot."),
            BotCommand("help", "Help message."),
            BotCommand("start", "Start message."),
            BotCommand("login", "Login to your account."),
            BotCommand("logout", "Logout from your account."),
        ],
    },
}

# حفظ الاوامر الافتراضية في مصفوفة
default_commands = [
    command.command for command in COMMANDS.get("ar").get(BotCommandScopeDefault)
]

# حفظ الاوامر الخاصة في مصفوفة
private_chat_commands = [
    command.command
    for command in COMMANDS.get("ar").get(BotCommandScopeAllPrivateChats)
]
