import os
from rubka import Robot, Message
from rubka.keypad import ChatKeypadBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")

await message.reply_keypad(
    "👋 سلام!\n\n"
    "به فروشگاه جم خوش اومدی 💎\n\n"
    "🛍 فروشگاه: @TRIX__SHOP\n"
    "🔗 https://rubika.ir/TRIX__SHOP\n\n"
    "از منوی زیر انتخاب کن:",
    main_menu()
)

# شماره کارت فعلی خودت را در همین خط نگه دار
CARD_NUMBER = "5022291575298169"
CARD_NAME = "رضا الله مددی آقبلاغی"

bot = Robot(token=BOT_TOKEN)
pending_orders = {}


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


def order_keypad(package_id):
    builder = ChatKeypadBuilder()
    return (
        builder
        .row(builder.button(id=f"confirm_{package_id}", text="✅ تأیید سفارش"))
        .row(builder.button(id="cancel_order", text="❌ لغو"))
        .build()
    )


PACKAGES = {
    "gem_110": {"name": "110 Gem", "price": "275✨", "type": "id"},
    "gem_231": {"name": "231 Gem", "price": "518✨", "type": "id"},
    "gem_583": {"name": "583 Gem", "price": "1375✨", "type": "id"},
    "gem_1060": {"name": "1060K Gem", "price": "2450✨", "type": "id"},
    "gem_2180": {"name": "2180K Gem", "price": "5,119✨", "type": "id"},
    "gem_5000": {"name": "5K Gem", "price": "12.3 MiL🌟", "type": "id"},
    "gem_11000": {"name": "11K GEM", "price": "23.890 MiL🌟", "type": "id"},
    "monthly_id": {"name": "Monthly", "price": "2.690💸", "type": "id"},
    "weekly_id": {"name": "Weekly", "price": "549💸", "type": "id"},

    "info_weekly": {"name": "هفتگی (450 جم)", "price": "369.000T💸", "type": "info"},
    "info_monthly": {"name": "ماهانه (2.600 جم)", "price": "1.950.000T💸", "type": "info"},
    "info_light": {"name": "هفتگی لایت (100 جم)", "price": "195.000T💸", "type": "info"},
    "offer_1": {"name": "آفر یک دلاری", "price": "220.000T💸", "type": "info"},
    "offer_2": {"name": "آفر دو دلاری", "price": "385.000T💸", "type": "info"},
    "levelup": {"name": "لول آپ پس (1250 Gem)", "price": "980", "type": "info"},
    "level_120": {"name": "120 جم", "price": "185", "type": "info"},
    "level_200": {"name": "200 جم", "price": "230", "type": "info"},
    "level_350": {"name": "350 جم", "price": "295", "type": "info"}
}


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


@bot.on_message()
async def normal_message(bot: Robot, message: Message):
    text = (message.text or "").strip()
    chat_id = message.chat_id

    if not text or text == "/start":
        return

    if chat_id not in pending_orders:
        return

    order = pending_orders[chat_id]
    step = order["step"]

    if step == "account_id":
        order["account_id"] = text
        order["step"] = "account_name"

        await message.reply(
            "✅ آیدی اکانت دریافت شد.\n\n"
            "👤 لطفاً نام اکانت را ارسال کنید:"
        )
        return

    if step == "account_name":
        order["account_name"] = text
        await send_payment_info(message, order)
        return

    if step == "gmail":
        order["gmail"] = text
        order["step"] = "support_info"

        await message.reply(
            "✅ Gmail دریافت شد.\n\n"
            "📸 لطفاً اطلاعات غیرحساس پشتیبانی/کد موردنیاز سفارش را ارسال کنید.\n\n"
            "⚠️ رمز عبور حساب را ارسال نکنید."
        )
        return

    if step == "support_info":
        order["support_info"] = text
        order["step"] = "account_id"

        await message.reply(
            "✅ اطلاعات پشتیبانی دریافت شد.\n\n"
            "🆔 لطفاً آیدی اکانت را ارسال کنید:"
        )
        return

    if step == "receipt":
        order["receipt"] = text
        order["step"] = "completed"

        await message.reply(
            "✅ رسید دریافت شد.\n\n"
            "📦 سفارش شما ثبت شد.\n"
            "⏳ وضعیت سفارش: در انتظار بررسی"
        )
        return


async def send_payment_info(message, order):
    order["step"] = "receipt"
    package = order["package"]

    await message.reply(
        "✅ اطلاعات سفارش کامل شد.\n\n"
        f"💎 محصول: {package['name']}\n"
        f"💰 مبلغ: {package['price']}\n\n"
        "💳 اطلاعات پرداخت\n"
        "━━━━━━━━━━━━━━\n\n"
        f"👤 نام صاحب کارت:\n{CARD_NAME}\n\n"
        f"💳 شماره کارت:\n{CARD_NUMBER}\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "💰 لطفاً مبلغ دقیق سفارش را واریز کنید.\n\n"
        "🧾 سپس رسید پرداخت را ارسال کنید."
    )


@bot.on_callback()
async def all_callbacks(bot: Robot, message: Message):
    try:
        button_id = message.aux_data.button_id
    except Exception:
        return

    chat_id = message.chat_id

    if button_id == "buy":
        await message.reply_keypad(
            "🛍 لیست جم با ایدی : 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )
        return

    if button_id == "next_page":
        await message.reply_keypad(
            "🛍 لیست جم با اطلاعات : 📌\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page2_keypad()
        )
        return

    if button_id == "back_page":
        await message.reply_keypad(
            "🛍 لیست جم با ایدی : 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )
        return

    if button_id == "cancel_order":
        if chat_id in pending_orders:
            del pending_orders[chat_id]

        await message.reply_keypad(
            "❌ سفارش لغو شد.\n\n"
            "🛍 می‌توانید دوباره یک بسته انتخاب کنید:",
            page1_keypad()
        )
        return

    if button_id in PACKAGES:
        package = PACKAGES[button_id]

        await message.reply_keypad(
            "🛍 سفارش شما\n\n"
            f"💎 بسته: {package['name']}\n"
            f"💰 قیمت: {package['price']}\n\n"
            "آیا این بسته را تأیید می‌کنید؟",
            order_keypad(button_id)
        )
        return

    if button_id.startswith("confirm_"):
        package_id = button_id.replace("confirm_", "", 1)

        if package_id not in PACKAGES:
            return

        package = PACKAGES[package_id]

        pending_orders[chat_id] = {
            "package": package,
            "package_id": package_id,
            "step": None
        }

        if package["type"] == "id":
            pending_orders[chat_id]["step"] = "account_id"

            await message.reply(
                "✅ سفارش تأیید شد.\n\n"
                f"💎 بسته: {package['name']}\n"
                f"💰 قیمت: {package['price']}\n\n"
                "🆔 لطفاً آیدی اکانت خود را ارسال کنید:"
            )
            return

        if package["type"] == "info":
            pending_orders[chat_id]["step"] = "gmail"

            await message.reply(
                "✅ سفارش تأیید شد.\n\n"
                f"💎 بسته: {package['name']}\n"
                f"💰 قیمت: {package['price']}\n\n"
                "📧 لطفاً Gmail مربوط به اکانت را ارسال کنید:\n\n"
                "⚠️ رمز عبور حساب را ارسال نکنید."
            )
            return

    if button_id == "orders":
        if chat_id in pending_orders:
            order = pending_orders[chat_id]

            await message.reply(
                "📦 سفارش فعال شما\n\n"
                f"💎 محصول: {order['package']['name']}\n"
                f"💰 مبلغ: {order['package']['price']}\n\n"
                "⏳ وضعیت: در حال تکمیل اطلاعات/بررسی"
            )
        else:
            await message.reply(
                "📦 در حال حاضر سفارش فعالی برای شما پیدا نشد."
            )
        return

    if button_id == "support":
        await message.reply(
            "🆘 برای پشتیبانی با مدیر فروشگاه در ارتباط باشید."
        )
        return


bot.run()
