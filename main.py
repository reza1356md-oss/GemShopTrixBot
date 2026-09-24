import os
from dotenv import load_dotenv
from rubka import Robot, Message
from rubka.keypad import ChatKeypadBuilder

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
SHOP_USERNAME = os.getenv("SHOP_USERNAME", "@TRIX__SHOP").strip()
SHOP_LINK = os.getenv("SHOP_LINK", "https://rubika.ir/TRIX__SHOP").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

bot = Robot(token=BOT_TOKEN)


def main_keypad():
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(builder.button(id="buy", text="🛒 خرید جم"))
        .row(builder.button(id="orders", text="📦 پیگیری سفارش"))
        .row(builder.button(id="support", text="💬 پشتیبانی"))
        .build()
    )


def send_home(message: Message):
    text = (
        "سلام 👋\n\n"
        "🛍️ به فروشگاه جم TRIX خوش آمدید. 💎\n\n"
        "از منوی زیر گزینه موردنظر را انتخاب کنید."
    )
    message.reply_keypad(text, main_keypad())


@bot.on_message(commands=["start"])
def start_handler(bot_instance: Robot, message: Message):
    send_home(message)


@bot.on_callback("buy")
def buy_handler(bot_instance: Robot, message: Message):
    message.reply(
        "🛒 بخش خرید جم\n\n"
        "این بخش در نسخه بعدی فعال می‌شود.\n"
        "در نسخه بعد، بسته‌های جم، قیمت، Player ID و ارسال رسید را اضافه می‌کنیم."
    )


@bot.on_callback("orders")
def orders_handler(bot_instance: Robot, message: Message):
    message.reply("📦 هنوز سفارشی برای پیگیری ثبت نشده است.")


@bot.on_callback("support")
def support_handler(bot_instance: Robot, message: Message):
    message.reply(
        "💬 پشتیبانی فروشگاه\n\n"
        "برای ارتباط با پشتیبانی، از راه ارتباطی اعلام‌شده توسط فروشگاه استفاده کنید."
    )


@bot.on_message()
def fallback_handler(bot_instance: Robot, message: Message):
    send_home(message)


if __name__ == "__main__":
    bot.set_commands([
        {"command": "start", "description": "شروع ربات"},
        {"command": "help", "description": "راهنما"},
    ])
    print("GemShopTrixBot is running...")
    bot.run()
