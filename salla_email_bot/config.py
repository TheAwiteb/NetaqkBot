"""
سوف يتم حفظ المتغيرات الاساسية في هذا الملف
"""
from password_strength import PasswordPolicy
from os import environ
from pathlib import Path
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
)

load_dotenv()

# password policy
length = 8  # min length: 10
uppercase = 1  # need min. 1 uppercase letters
numbers = 1  # need min. 1 digits
special = 1  # need min. 1 special characters

similarity2username = (
    65 / 100
)  # Percentage password similarity to username, default is 65%

password_policy = PasswordPolicy.from_names(
    length=length,
    uppercase=uppercase,
    numbers=numbers,
    special=special,
)


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

# BASE_DIR is: path_to/salla_email_bot/salla_email_bot
BASE_DIR = Path(__file__).parent

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
            BotCommand("reset_password", "اعادة تعيين كلمة المرور."),
            BotCommand("cancel", "لالغاء العملية."),
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
            BotCommand("reset_password", "Reset password."),
            BotCommand("cancel", "For cancel the process."),
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
