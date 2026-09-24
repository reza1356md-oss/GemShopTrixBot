import os
from dotenv import load_dotenv
from rubka import Robot, filters
from rubka.context import Message
from rubka.keypad import ChatKeypadBuilder

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHOP_USERNAME = os.getenv("SHOP_USERNAME", "@TRIX__SHOP")
SHOP_LINK = os.getenv("SHOP_LINK", "https://rubika.ir/TRIX__SHOP")

bot = Robot(BOT_TOKEN)


def main_menu():
    return (
        ChatKeypadBuilder()
        .row(
            ("💎 خرید جم", "buy"),
            ("📦 پیگیری سفارش", "orders"),
        )
        .row(
            ("🆘 پشتیبانی", "support"),
        )
        .build()
    )


@bot.on_message(filters.Commands("start"))
async def start_handler(bot, message: Message):
    text = (
        "👋 سلام!\n\n"
        "به فروشگاه جم خوش اومدی 💎\n"
        f"کانال فروشگاه: {SHOP_USERNAME}\n\n"
        "از منوی زیر یکی از گزینه‌ها رو انتخاب کن:"
    )
    await message.reply(text, chat_keypad=main_menu())


@bot.on_callback_query()
async def callback_handler(bot, query):
    data = getattr(query, "data", "")
    message = getattr(query, "message", None)

    if data == "buy":
        text = (
            "💎 خرید جم\n\n"
            "به‌زودی لیست بسته‌های جم و قیمت‌ها اینجا نمایش داده می‌شود."
        )
    elif data == "orders":
        text = "📦 پیگیری سفارش\n\nفعلاً سیستم پیگیری سفارش در حال آماده‌سازی است."
    elif data == "support":
        text = "🆘 پشتیبانی\n\nبرای پشتیبانی با مدیر فروشگاه در ارتباط باشید."
    else:
        return

    if message:
        await message.reply(text)


@bot.on_message()
async def fallback_handler(bot, message: Message):
    if getattr(message, "text", ""):
        await message.reply(
            "لطفاً از منوی اصلی یکی از گزینه‌ها را انتخاب کن.",
            chat_keypad=main_menu(),
        )


bot.set_commands([
    ("start", "شروع کار با فروشگاه"),
])

bot.run()
