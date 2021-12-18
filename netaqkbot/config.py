"""
سوف يتم حفظ المتغيرات الاساسية في هذا الملف
"""
from password_strength import PasswordPolicy
from os import environ
from pathlib import Path
from dotenv import load_dotenv
from threading import Event
from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager, CaptchaOptions, CustomLanguage
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


plans = [
    "free",
    "bronze",
    "silver",
    "golden",
    "diamond",
    "admin",
]

# تعديل بعض الحقول في اللغة الخاصة بالتحقق
custom_language = CustomLanguage(
    base_language="ar",
    text="اهلا #USER عذرا لازعاجك ولكن لمتابعة تسجيل الدخول يجب التاكد من انك مستخدم حقيقي",
)
# تعريف اوبجكت الخيارات
options = CaptchaOptions(
    generator="default",  # نوع منشئ الصور
    add_noise=False,  # اضافة تشويش للصورة
    only_digits=True,  # استخدام الارقام فقط
    code_length=6,  # طول رسالة التحقق
    max_attempts=2,  # عدد المحاولات
    max_user_reloads=3,  # عدد تغير الصورة
    custom_language=custom_language,  # اللغة (اللغة العربية موجودة بالفعل، ولكن تم تعديل رسالة التحقق اعلاه)
)

unique_code_length = 5
default_language = "ar"
space_url_char = "spss"

# for `using_limit` and `session_time` infinity is 0
max_using_limit = 4  # using the url 'reset_password' and 'register'
default_session_timeout = (3 * 60) * 60  # 3h in seconds
max_session_timeout = 5  # 5h

check_timeout_delay = 3 * 60  # 3m
exit_event = Event()

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

# BASE_DIR is: path_to/NetaqkBot/netaqkbot
BASE_DIR = Path(__file__).parent

# البوت
BOT: TeleBot = TeleBot(TOKEN)

# مدير التحقق
captcha_manager = CaptchaManager(BOT.get_me().id, default_options=options)

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
