import os
from dotenv import load_dotenv
from rubka import Robot, Message
from rubka.keypad import ChatKeypadBuilder

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_GUID = os.getenv("CHANNEL_GUID", "").strip()
SHOP_USERNAME = os.getenv("SHOP_USERNAME", "@TRIX__SHOP").strip()
SHOP_LINK = os.getenv("SHOP_LINK", "https://rubika.ir/TRIX__SHOP").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN در فایل .env تنظیم نشده است.")

if not CHANNEL_GUID:
    raise RuntimeError(
        "CHANNEL_GUID در فایل .env تنظیم نشده است. "
        "شناسه (GUID) کانال @TRIX__SHOP را وارد کنید."
    )

bot = Robot(token=BOT_TOKEN)


def join_keypad():
    builder = ChatKeypadBuilder()
    return builder.row(
        builder.button(id="check_join", text="✅ بررسی عضویت")
    ).build()


def main_keypad():
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(builder.button(id="buy", text="🛒 خرید جم"))
        .row(builder.button(id="orders", text="📦 پیگیری سفارش"))
        .row(builder.button(id="support", text="💬 پشتیبانی"))
        .build()
    )


def is_joined(chat_id: str) -> bool:
    try:
        return bool(bot.check_join(CHANNEL_GUID, chat_id))
    except Exception as exc:
        print(f"[JOIN CHECK ERROR] {exc}")
        return False


def send_join_message(message: Message):
    text = (
        "سلام 👋\n\n"
        "به فروشگاه جم TRIX خوش آمدید. 💎\n\n"
        "برای استفاده از ربات ابتدا باید عضو شاپ ما شوید:\n"
        f"{SHOP_LINK}\n\n"
        "بعد از عضویت، روی «بررسی عضویت» بزنید."
    )
    message.reply_keypad(text, join_keypad())


def send_home(message: Message):
    text = (
        "✅ عضویت شما تأیید شد.\n\n"
        "🛍️ به فروشگاه جم TRIX خوش آمدید.\n"
        "از منوی زیر گزینه موردنظر را انتخاب کنید."
    )
    message.reply_keypad(text, main_keypad())


@bot.on_message(commands=["start"])
def start_handler(bot_instance: Robot, message: Message):
    if is_joined(message.chat_id):
        send_home(message)
    else:
        send_join_message(message)


@bot.on_callback("check_join")
def check_join_handler(bot_instance: Robot, message: Message):
    if is_joined(message.chat_id):
        send_home(message)
    else:
        message.reply(
            "❌ هنوز عضویت شما تأیید نشده است.\n\n"
            f"ابتدا عضو {SHOP_USERNAME} شوید و سپس دوباره روی "
            "«بررسی عضویت» بزنید."
        )


@bot.on_callback("buy")
def buy_handler(bot_instance: Robot, message: Message):
    if not is_joined(message.chat_id):
        send_join_message(message)
        return

    message.reply(
        "🛒 بخش خرید جم\n\n"
        "این بخش در نسخه بعدی فعال می‌شود.\n"
        "در نسخه بعد، بسته‌های جم، قیمت، Player ID و ارسال رسید را اضافه می‌کنیم."
    )


@bot.on_callback("orders")
def orders_handler(bot_instance: Robot, message: Message):
    if not is_joined(message.chat_id):
        send_join_message(message)
        return

    message.reply("📦 هنوز سفارشی برای پیگیری ثبت نشده است.")


@bot.on_callback("support")
def support_handler(bot_instance: Robot, message: Message):
    message.reply(
        "💬 پشتیبانی فروشگاه\n\n"
        "برای ارتباط با پشتیبانی، از راه ارتباطی اعلام‌شده توسط فروشگاه استفاده کنید."
    )


@bot.on_message()
def fallback_handler(bot_instance: Robot, message: Message):
    # اگر کاربر /start یا دکمه‌ها را استفاده نکرد، وضعیت عضویت را یادآوری می‌کنیم.
    if not is_joined(message.chat_id):
        send_join_message(message)
    else:
        send_home(message)


if __name__ == "__main__":
    bot.set_commands([
        {"command": "start", "description": "شروع ربات"},
        {"command": "help", "description": "راهنما"},
    ])
    print("GemShopTrixBot is running...")
    bot.run()
