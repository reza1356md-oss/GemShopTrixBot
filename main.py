import os
from rubka import Robot, Message
from rubka.keypad import ChatKeypadBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHOP_USERNAME = os.getenv("SHOP_USERNAME", "@TRIX__SHOP")
SHOP_LINK = os.getenv("SHOP_LINK", "https://rubika.ir/TRIX__SHOP")

bot = Robot(token=BOT_TOKEN)


def main_menu():
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(
            builder.button(id="buy", text="💎 خرید جم"),
            builder.button(id="orders", text="📦 پیگیری سفارش")
        )
        .row(
            builder.button(id="support", text="🆘 پشتیبانی")
        )
        .build()
    )


@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):
    await message.reply_keypad(
        "👋 سلام!\n\n"
        "به فروشگاه جم خوش اومدی 💎\n\n"
        f"🛍 فروشگاه: {SHOP_USERNAME}\n"
        f"🔗 {SHOP_LINK}\n\n"
        "یکی از گزینه‌های زیر رو انتخاب کن:",
        main_menu()
    )


@bot.on_callback("buy")
def buy(bot: Robot, message: Message):
    message.reply(
        "💎 خرید جم\n\n"
        "لیست بسته‌های جم به‌زودی اضافه می‌شود."
    )


@bot.on_callback("orders")
def orders(bot: Robot, message: Message):
    message.reply(
        "📦 پیگیری سفارش\n\n"
        "سیستم پیگیری سفارش به‌زودی فعال می‌شود."
    )


@bot.on_callback("support")
def support(bot: Robot, message: Message):
    message.reply(
        "🆘 پشتیبانی\n\n"
        "برای پشتیبانی به مدیر فروشگاه پیام بده."
    )


bot.run()
