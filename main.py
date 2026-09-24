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


def page1_keypad():
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(builder.button(id="gem_110", text="💎 110 Gem — 275✨"))
        .row(builder.button(id="gem_231", text="💎 231 Gem — 518✨"))
        .row(builder.button(id="gem_583", text="💎 583 Gem — 1375✨"))
        .row(builder.button(id="gem_1060", text="💎 1060K Gem — 2450✨"))
        .row(builder.button(id="gem_2180", text="💎 2180K Gem — 5,119✨"))
        .row(builder.button(id="gem_5000", text="💎 5K Gem — 12.3 MiL🌟"))
        .row(builder.button(id="gem_11000", text="💎 11K GEM — 23.890 MiL🌟"))
        .row(builder.button(id="monthly_id", text="📆 Monthly — 2.690💸"))
        .row(builder.button(id="weekly_id", text="🗓 Weekly — 549💸"))
        .row(builder.button(id="next_page", text="➡️ صفحه دوم"))
        .build()
    )


def page2_keypad():
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(builder.button(id="info_weekly", text="📌 هفتگی 450 جم — 369.000T💸"))
        .row(builder.button(id="info_monthly", text="📌 ماهانه 2.600 جم — 1.950.000T💸"))
        .row(builder.button(id="info_light", text="📌 هفتگی لایت 100 جم — 195.000T💸"))
        .row(builder.button(id="offer_1", text="🎁 آفر یک دلاری — 220.000T💸"))
        .row(builder.button(id="offer_2", text="🎁 آفر دو دلاری — 385.000T💸"))
        .row(builder.button(id="levelup", text="🏵 لول آپ پس 1250 Gem — 980"))
        .row(builder.button(id="level_120", text="⚠️ 120 جم — 185"))
        .row(builder.button(id="level_200", text="⚠️ 200 جم — 230"))
        .row(builder.button(id="level_350", text="⚠️ 350 جم — 295"))
        .row(builder.button(id="back_page", text="⬅️ صفحه اول"))
        .build()
    )


def order_keypad(confirm_id):
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(
            builder.button(id=confirm_id, text="✅ تأیید سفارش")
        )
        .row(
            builder.button(id="cancel_order", text="❌ لغو")
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
        "از منوی زیر انتخاب کن:",
        main_menu()
    )


@bot.on_callback("buy")
async def buy(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 لیست جم با ایدی : 💎\n\n"
        "بسته موردنظر را انتخاب کنید:",
        page1_keypad()
    )


@bot.on_callback("next_page")
async def next_page(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 لیست جم با اطلاعات : 📌\n\n"
        "بسته موردنظر را انتخاب کنید:",
        page2_keypad()
    )


@bot.on_callback("back_page")
async def back_page(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 لیست جم با ایدی : 💎\n\n"
        "بسته موردنظر را انتخاب کنید:",
        page1_keypad()
    )


@bot.on_callback("gem_110")
async def gem_110(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 110 Gem\n"
        "💰 قیمت: 275✨\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_110")
    )


@bot.on_callback("confirm_110")
async def confirm_110(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 110 Gem\n"
        "💰 قیمت: 275✨\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("gem_231")
async def gem_231(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 231 Gem\n"
        "💰 قیمت: 518✨\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_231")
    )


@bot.on_callback("confirm_231")
async def confirm_231(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 231 Gem\n"
        "💰 قیمت: 518✨\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("gem_583")
async def gem_583(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 583 Gem\n"
        "💰 قیمت: 1375✨\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_583")
    )


@bot.on_callback("confirm_583")
async def confirm_583(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 583 Gem\n"
        "💰 قیمت: 1375✨\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("gem_1060")
async def gem_1060(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 1060K Gem\n"
        "💰 قیمت: 2450✨\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_1060")
    )


@bot.on_callback("confirm_1060")
async def confirm_1060(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 1060K Gem\n"
        "💰 قیمت: 2450✨\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("gem_2180")
async def gem_2180(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 2180K Gem\n"
        "💰 قیمت: 5,119✨\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_2180")
    )


@bot.on_callback("confirm_2180")
async def confirm_2180(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 2180K Gem\n"
        "💰 قیمت: 5,119✨\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("gem_5000")
async def gem_5000(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 5K Gem\n"
        "💰 قیمت: 12.3 MiL🌟\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_5000")
    )


@bot.on_callback("confirm_5000")
async def confirm_5000(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 5K Gem\n"
        "💰 قیمت: 12.3 MiL🌟\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("gem_11000")
async def gem_11000(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 11K GEM\n"
        "💰 قیمت: 23.890 MiL🌟\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_11000")
    )


@bot.on_callback("confirm_11000")
async def confirm_11000(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 11K GEM\n"
        "💰 قیمت: 23.890 MiL🌟\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("monthly_id")
async def monthly_id(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "📆 بسته: Monthly\n"
        "💰 قیمت: 2.690💸\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_monthly")
    )


@bot.on_callback("confirm_monthly")
async def confirm_monthly(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "📆 بسته: Monthly\n"
        "💰 قیمت: 2.690💸\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("weekly_id")
async def weekly_id(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "🗓 بسته: Weekly\n"
        "💰 قیمت: 549💸\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_weekly")
    )


@bot.on_callback("confirm_weekly")
async def confirm_weekly(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "🗓 بسته: Weekly\n"
        "💰 قیمت: 549💸\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("info_weekly")
async def info_weekly(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "📌 بسته: هفتگی (450 جم)\n"
        "💰 قیمت: 369.000T💸\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_info_weekly")
    )


@bot.on_callback("confirm_info_weekly")
async def confirm_info_weekly(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "📌 بسته: هفتگی (450 جم)\n"
        "💰 قیمت: 369.000T💸\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("info_monthly")
async def info_monthly(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "📌 بسته: ماهانه (2.600 جم)\n"
        "💰 قیمت: 1.950.000T💸\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_info_monthly")
    )


@bot.on_callback("confirm_info_monthly")
async def confirm_info_monthly(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "📌 بسته: ماهانه (2.600 جم)\n"
        "💰 قیمت: 1.950.000T💸\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("info_light")
async def info_light(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "📌 بسته: هفتگی لایت (100 جم)\n"
        "💰 قیمت: 195.000T💸\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_info_light")
    )


@bot.on_callback("confirm_info_light")
async def confirm_info_light(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "📌 بسته: هفتگی لایت (100 جم)\n"
        "💰 قیمت: 195.000T💸\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("offer_1")
async def offer_1(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "🎁 بسته: آفر یک دلاری\n"
        "💰 قیمت: 220.000T💸\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_offer_1")
    )


@bot.on_callback("confirm_offer_1")
async def confirm_offer_1(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "🎁 بسته: آفر یک دلاری\n"
        "💰 قیمت: 220.000T💸\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("offer_2")
async def offer_2(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "🎁 بسته: آفر دو دلاری\n"
        "💰 قیمت: 385.000T💸\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_offer_2")
    )


@bot.on_callback("confirm_offer_2")
async def confirm_offer_2(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "🎁 بسته: آفر دو دلاری\n"
        "💰 قیمت: 385.000T💸\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("levelup")
async def levelup(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "🏵 بسته: لول آپ پس (1250 Gem)\n"
        "💰 قیمت: 980\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_levelup")
    )


@bot.on_callback("confirm_levelup")
async def confirm_levelup(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "🏵 بسته: لول آپ پس (1250 Gem)\n"
        "💰 قیمت: 980\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("level_120")
async def level_120(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 120 جم\n"
        "💰 قیمت: 185\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_level_120")
    )


@bot.on_callback("confirm_level_120")
async def confirm_level_120(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 120 جم\n"
        "💰 قیمت: 185\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("level_200")
async def level_200(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 200 جم\n"
        "💰 قیمت: 230\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_level_200")
    )


@bot.on_callback("confirm_level_200")
async def confirm_level_200(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 200 جم\n"
        "💰 قیمت: 230\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("level_350")
async def level_350(bot: Robot, message: Message):
    await message.reply_keypad(
        "🛍 سفارش شما\n\n"
        "💎 بسته: 350 جم\n"
        "💰 قیمت: 295\n\n"
        "آیا این بسته را تأیید می‌کنید؟",
        order_keypad("confirm_level_350")
    )


@bot.on_callback("confirm_level_350")
async def confirm_level_350(bot: Robot, message: Message):
    await message.reply(
        "✅ سفارش شما ثبت شد.\n\n"
        "💎 بسته: 350 جم\n"
        "💰 قیمت: 295\n\n"
        "📦 وضعیت سفارش: در انتظار پرداخت"
    )


@bot.on_callback("cancel_order")
async def cancel_order(bot: Robot, message: Message):
    await message.reply_keypad(
        "❌ سفارش لغو شد.\n\n"
        "🛍 می‌توانید دوباره یک بسته انتخاب کنید:",
        page1_keypad()
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
