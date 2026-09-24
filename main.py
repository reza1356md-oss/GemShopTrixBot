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


def gems_page_1():
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(builder.button(id="gem_110", text="🛒 خرید 110 جم"))
        .row(builder.button(id="gem_231", text="🛒 خرید 231 جم"))
        .row(builder.button(id="gem_583", text="🛒 خرید 583 جم"))
        .row(builder.button(id="gem_1060", text="🛒 خرید 1060K جم"))
        .row(builder.button(id="gem_2180", text="🛒 خرید 2180K جم"))
        .row(builder.button(id="next_page", text="➡️ صفحه بعدی"))
        .build()
    )


@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):
    await message.reply_keypad(
        "👋 سلام!\n\n"
        "به فروشگاه جم خوش اومدی 💎\n\n"
        f"🛍 فروشگاه: {SHOP_USERNAME}\n"
        f"🔗 {SHOP_LINK}\n\n"
        "از منوی زیر انتخاب کن:",
        main_menu()
    )


@bot.on_callback("buy")
async def buy(bot: Robot, message: Message):
    text = (
        "💎 لیست جم - صفحه 1 از 2\n\n"
        "💎 110 Gem — 275✨\n"
        "💎 231 Gem — 518✨\n"
        "💎 583 Gem — 1375✨\n"
        "💎 1060K Gem — 2450✨\n"
        "💎 2180K Gem — 5,119✨\n\n"
        "برای خرید، بسته موردنظر را انتخاب کن:"
    )
    await message.reply_keypad(text, gems_page_1())


@bot.on_callback("gem_110")
async def gem_110(bot: Robot, message: Message):
    await message.reply(
        "🛒 انتخاب شد: 110 Gem — 275✨\n\n"
        "برای تکمیل خرید، پشتیبانی با شما ارتباط خواهد گرفت."
    )


@bot.on_callback("gem_231")
async def gem_231(bot: Robot, message: Message):
    await message.reply(
        "🛒 انتخاب شد: 231 Gem — 518✨\n\n"
        "برای تکمیل خرید، پشتیبانی با شما ارتباط خواهد گرفت."
    )


@bot.on_callback("gem_583")
async def gem_583(bot: Robot, message: Message):
    await message.reply(
        "🛒 انتخاب شد: 583 Gem — 1375✨\n\n"
        "برای تکمیل خرید، پشتیبانی با شما ارتباط خواهد گرفت."
    )


@bot.on_callback("gem_1060")
async def gem_1060(bot: Robot, message: Message):
    await message.reply(
        "🛒 انتخاب شد: 1060K Gem — 2450✨\n\n"
        "برای تکمیل خرید، پشتیبانی با شما ارتباط خواهد گرفت."
    )


@bot.on_callback("gem_2180")
async def gem_2180(bot: Robot, message: Message):
    await message.reply(
        "🛒 انتخاب شد: 2180K Gem — 5,119✨\n\n"
        "برای تکمیل خرید، پشتیبانی با شما ارتباط خواهد گرفت."
    )


@bot.on_callback("next_page")
async def next_page(bot: Robot, message: Message):
    await message.reply(
        "⏳ صفحه دوم به‌زودی اضافه می‌شود."
    )


@bot.on_callback("orders")
async def orders(bot: Robot, message: Message):
    await message.reply(
        "📦 سیستم پیگیری سفارش به‌زودی فعال می‌شود."
    )


@bot.on_callback("support")
async def support(bot: Robot, message: Message):
    await message.reply(
        "🆘 برای پشتیبانی با مدیر فروشگاه در ارتباط باشید."
    )


bot.run()
