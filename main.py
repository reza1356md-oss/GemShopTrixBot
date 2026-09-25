import os
import random
import re

from rubka import Robot, Message
from rubka.keypad import ChatKeypadBuilder


# ==================================================
# تنظیمات
# ==================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

SHOP_USERNAME = "@TRIX__SHOP"
SHOP_LINK = "https://rubika.ir/TRIX__SHOP"
GROUP_LINK = "https://rubika.ir/joing/JHGBHFGG0PKMOKLLUWKSWHNFELZKLBUJ"

# شماره کارت خودت را اینجا قرار بده
CARD_NUMBER = "5022291575298169"

CARD_NAME = "رضا الله مددی آقبلاغی"

ADMIN_CHAT_ID = "b0KG4TR0BGyi09906a6a3aa2c8fc9c47"


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN در Railway تنظیم نشده است.")


bot = Robot(token=BOT_TOKEN)


# ==================================================
# ذخیره موقت سفارش‌ها
# ==================================================

pending_orders = {}
orders_by_tracking = {}
used_tracking_codes = set()

# وقتی مدیر روی رد رسید می‌زند
admin_reject_waiting = {}


# ==================================================
# کد پیگیری
# ==================================================

def generate_tracking_code():

    while True:

        code = f"#{random.randint(100000, 999999)}"

        if code not in used_tracking_codes:

            used_tracking_codes.add(code)

            return code


# ==================================================
# لیست بسته‌ها
# ==================================================

PACKAGES = {

    # ==============================================
    # صفحه اول - جم با آیدی
    # ==============================================

    "id_1": {
        "name": "💎 100 جم",
        "price": "20,000 تومان",
        "type": "id"
    },

    "id_2": {
        "name": "💎 200 جم",
        "price": "40,000 تومان",
        "type": "id"
    },

    "id_3": {
        "name": "💎 500 جم",
        "price": "90,000 تومان",
        "type": "id"
    },

    "id_4": {
        "name": "💎 1000 جم",
        "price": "170,000 تومان",
        "type": "id"
    },


    # ==============================================
    # صفحه دوم - جم با اطلاعات
    # ==============================================

    "info_1": {
        "name": "💎 100 جم اطلاعات",
        "price": "20,000 تومان",
        "type": "info"
    },

    "info_2": {
        "name": "💎 200 جم اطلاعات",
        "price": "40,000 تومان",
        "type": "info"
    },

    "info_3": {
        "name": "💎 500 جم اطلاعات",
        "price": "90,000 تومان",
        "type": "info"
    },

    "info_4": {
        "name": "💎 1000 جم اطلاعات",
        "price": "170,000 تومان",
        "type": "info"
    }
}


# ==================================================
# منوی اصلی
# ==================================================

def main_keypad():

    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(
                "buy_gem",
                "💎 خرید جم"
            )
        )
        .row(
            ChatKeypadBuilder().button(
                "track_order",
                "🎫 پیگیری سفارش"
            ),
            ChatKeypadBuilder().button(
                "support",
                "🆘 پشتیبانی"
            )
        )
        .build()
    )


# ==================================================
# صفحه اول - جم با آیدی
# ==================================================

def id_packages_keypad():

    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(
                "buy_id_1",
                PACKAGES["id_1"]["name"]
            ),
            ChatKeypadBuilder().button(
                "buy_id_2",
                PACKAGES["id_2"]["name"]
            )
        )
        .row(
            ChatKeypadBuilder().button(
                "buy_id_3",
                PACKAGES["id_3"]["name"]
            ),
            ChatKeypadBuilder().button(
                "buy_id_4",
                PACKAGES["id_4"]["name"]
            )
        )
        .row(
            ChatKeypadBuilder().button(
                "next_info_page",
                "➡️ صفحه دوم"
            )
        )
        .row(
            ChatKeypadBuilder().button(
                "back_main",
                "🔙 بازگشت"
            )
        )
        .build()
    )


# ==================================================
# صفحه دوم - جم با اطلاعات
# ==================================================

def info_packages_keypad():

    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(
                "buy_info_1",
                PACKAGES["info_1"]["name"]
            ),
            ChatKeypadBuilder().button(
                "buy_info_2",
                PACKAGES["info_2"]["name"]
            )
        )
        .row(
            ChatKeypadBuilder().button(
                "buy_info_3",
                PACKAGES["info_3"]["name"]
            ),
            ChatKeypadBuilder().button(
                "buy_info_4",
                PACKAGES["info_4"]["name"]
            )
        )
        .row(
            ChatKeypadBuilder().button(
                "back_id_page",
                "⬅️ صفحه اول"
            )
        )
        .build()
    )


# ==================================================
# تأیید / لغو سفارش
# ==================================================

def order_keypad(package_id):

    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(
                f"confirm_{package_id}",
                "✅ تأیید سفارش"
            ),
            ChatKeypadBuilder().button(
                "cancel_order",
                "❌ لغو"
            )
        )
        .build()
    )


# ==================================================
# کی‌پد مدیر - تأیید / رد رسید
# ==================================================

def admin_receipt_keypad(tracking_code):

    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(
                f"admin_approve_{tracking_code}",
                "✅ تأیید رسید"
            ),
            ChatKeypadBuilder().button(
                f"admin_reject_{tracking_code}",
                "❌ رد رسید"
            )
        )
        .build()
    )


# ==================================================
# کی‌پد مدیر - انجام شد
# ==================================================

def admin_done_keypad(tracking_code):

    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(
                f"admin_done_{tracking_code}",
                "✅ انجام شد"
            )
        )
        .build()
    )


# ==================================================
# START
# ==================================================

@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):

    chat_id = message.chat_id

    pending_orders.pop(chat_id, None)

    await message.reply_keypad(

        "🤖 ربات خرید جم تریکس شاپ خوش آمدید 🫠\n\n"

        "📢 چنل اصلی اگهی اکانت : 👇\n"
        f"{SHOP_USERNAME}\n\n"

        "💬 گپ اصلی شاپ : 👇\n"
        f"{GROUP_LINK}\n\n"

        "از منوی زیر انتخاب کنید:",

        main_keypad()
    )


# ==================================================
# MYID
# ==================================================

@bot.on_message(commands=["myid"])
async def myid(bot: Robot, message: Message):

    await message.reply(
        f"🆔 آیدی چت شما:\n\n{message.chat_id}"
    )


# ==================================================
# پیام‌های متنی
# ==================================================

@bot.on_message()
async def normal_message(bot: Robot, message: Message):

    chat_id = message.chat_id

    text = (message.text or "").strip()


    # ==================================================
    # پیام مدیر
    # ==================================================

    if chat_id == ADMIN_CHAT_ID:

        # ----------------------------------------------
        # دلیل رد رسید
        # ----------------------------------------------

        if chat_id in admin_reject_waiting:

            if not text:

                await message.reply(
                    "⚠️ لطفاً دلیل رد رسید را به صورت متنی ارسال کنید."
                )

                return


            tracking_code = admin_reject_waiting[chat_id]

            order = orders_by_tracking.get(tracking_code)


            if not order:

                del admin_reject_waiting[chat_id]

                await message.reply(
                    "❌ سفارش پیدا نشد."
                )

                return


            customer_chat_id = order["chat_id"]


            order["reject_reason"] = text

            order["status"] = "rejected"

            order["step"] = "rejected"


            del admin_reject_waiting[chat_id]


            # ارسال دلیل برای مشتری

            await bot.send_message(

                customer_chat_id,

                "❌ رسید پرداخت سفارش شما تأیید نشد.\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "📝 توضیحات مدیریت:\n"
                f"{text}\n\n"

                "لطفاً پس از بررسی توضیحات، "
                "در صورت نیاز رسید صحیح را ارسال کنید."
            )


            await message.reply(

                "❌ رسید سفارش رد شد.\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "📝 دلیل برای مشتری ارسال شد."
            )

            return


        return


    # ==================================================
    # اگر مشتری سفارش ندارد
    # ==================================================

    if chat_id not in pending_orders:

        return


    order = pending_orders[chat_id]


    # ==================================================
    # آیدی اکانت - جم با آیدی
    # ==================================================

    if order["step"] == "account_id":

        if not text:

            await message.reply(
                "⚠️ لطفاً آیدی اکانت را ارسال کنید."
            )

            return


        order["account_id"] = text

        order["step"] = "account_name"


        await message.reply(
            "👤 حالا اسم اکانت را ارسال کنید:"
        )

        return


    # ==================================================
    # اسم اکانت - جم با آیدی
    # ==================================================

    if order["step"] == "account_name":

        if not text:

            await message.reply(
                "⚠️ لطفاً اسم اکانت را ارسال کنید."
            )

            return


        order["account_name"] = text

        await send_payment_info(chat_id)

        return


    # ==================================================
    # جیمیل - جم با اطلاعات
    # ==================================================

    if order["step"] == "gmail":

        if not text:

            await message.reply(
                "⚠️ لطفاً آدرس جی‌میل را ارسال کنید."
            )

            return


        if not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            text
        ):

            await message.reply(
                "❌ فرمت ایمیل درست نیست.\n\n"
                "لطفاً فقط آدرس جی‌میل را ارسال کنید."
            )

            return


        order["gmail"] = text

        order["step"] = "support_info"


        await message.reply(
            "📸 حالا اطلاعات پشتیبانی موردنیاز را ارسال کنید:"
        )

        return


    # ==================================================
    # اطلاعات پشتیبانی
    # ==================================================

    if order["step"] == "support_info":

        if not text:

            await message.reply(
                "⚠️ لطفاً اطلاعات پشتیبانی را ارسال کنید."
            )

            return


        order["support_info"] = text

        order["step"] = "support_image"


        await message.reply(
            "📸 حالا شات 10 تایی پشتیبانی را به صورت عکس ارسال کنید:"
        )

        return


    # ==================================================
    # اسم اکانت - جم با اطلاعات
    # ==================================================

    if order["step"] == "account_name_info":

        if not text:

            await message.reply(
                "⚠️ لطفاً اسم اکانت را ارسال کنید."
            )

            return


        order["account_name"] = text

        order["step"] = "account_id_info"


        await message.reply(
            "🆔 حالا آیدی اکانت را ارسال کنید:"
        )

        return


    # ==================================================
    # آیدی اکانت - جم با اطلاعات
    # ==================================================

    if order["step"] == "account_id_info":

        if not text:

            await message.reply(
                "⚠️ لطفاً آیدی اکانت را ارسال کنید."
            )

            return


        order["account_id"] = text

        await send_payment_info(chat_id)

        return


    # ==================================================
    # رسید متنی
    # ==================================================

    if order["step"] == "waiting_receipt":

        if not text:

            return


        await register_receipt(

            chat_id,

            receipt_text=text,

            receipt_image=False
        )

        return


# ==================================================
# هندلر عکس
# ==================================================

@bot.on_message()
async def support_image_handler(bot: Robot, message: Message):

    chat_id = message.chat_id

    if chat_id == ADMIN_CHAT_ID:
        return


    if chat_id not in pending_orders:
        return


    order = pending_orders[chat_id]


    # ==================================================
    # عکس شات پشتیبانی
    # ==================================================

    if order["step"] == "support_image":

        order["support_image"] = True

        order["step"] = "account_name_info"


        await message.reply(

            "📸 شات پشتیبانی دریافت شد ✅\n\n"

            "👤 حالا اسم اکانت را ارسال کنید:"
        )

        return


    # ==================================================
    # عکس رسید پرداخت
    # ==================================================

    if order["step"] == "waiting_receipt":

        await register_receipt(

            chat_id,

            receipt_text=None,

            receipt_image=True
        )

        return


# ==================================================
# ارسال اطلاعات پرداخت
# ==================================================

async def send_payment_info(chat_id):

    order = pending_orders.get(chat_id)

    if not order:
        return


    package = order["package"]


    order["step"] = "waiting_receipt"

    order["status"] = "waiting_receipt"


    await bot.send_message(

        chat_id,

        "💳 اطلاعات پرداخت\n\n"

        f"💎 بسته:\n"
        f"{package['name']}\n\n"

        f"💰 مبلغ:\n"
        f"{package['price']}\n\n"

        "👤 صاحب کارت:\n"
        f"{CARD_NAME}\n\n"

        "💳 شماره کارت:\n"
        f"{CARD_NUMBER}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "🧾 لطفاً بعد از پرداخت، "
        "رسید پرداخت را به صورت عکس یا متن ارسال کنید."
    )


# ==================================================
# ثبت رسید
# ==================================================

async def register_receipt(
    chat_id,
    receipt_text=None,
    receipt_image=False
):

    order = pending_orders.get(chat_id)

    if not order:
        return


    # ----------------------------------------------
    # ساخت کد پیگیری
    # ----------------------------------------------

    tracking_code = order.get("tracking_code")


    if not tracking_code:

        tracking_code = generate_tracking_code()

        order["tracking_code"] = tracking_code

        orders_by_tracking[tracking_code] = order


    # ----------------------------------------------
    # ذخیره رسید
    # ----------------------------------------------

    if receipt_text:

        order["receipt_text"] = receipt_text


    if receipt_image:

        order["receipt_image"] = True


    # ----------------------------------------------
    # وضعیت
    # ----------------------------------------------

    order["step"] = "waiting_confirmation"

    order["status"] = "waiting_confirmation"


    # ----------------------------------------------
    # پیام به مشتری
    # ----------------------------------------------

    await send_receipt_received_message(

        chat_id,

        tracking_code
    )


    # ----------------------------------------------
    # ارسال برای مدیر
    # ----------------------------------------------

    await notify_admin(

        tracking_code
    )


# ==================================================
# پیام دریافت رسید برای مشتری
# ==================================================

async def send_receipt_received_message(
    chat_id,
    tracking_code
):

    await bot.send_message(

        chat_id,

        "🧾 رسید پرداخت شما دریافت شد ✅\n\n"

        "📦 سفارش شما با موفقیت ثبت شد.\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "⏳ وضعیت سفارش شما:\n"
        "در انتظار تأیید رسید\n\n"

        "🎫 کد پیگیری سفارش:\n"
        f"{tracking_code}\n\n"

        "💎 لطفاً این کد پیگیری را نزد خود نگه دارید.\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "🙏 ممنون از اعتماد شما به TRIX SHOP ❤️"
    )


# ==================================================
# ارسال سفارش به مدیر
# ==================================================

async def notify_admin(tracking_code):

    order = orders_by_tracking.get(tracking_code)

    if not order:
        return


    package = order["package"]


    admin_text = (

        "🔔 سفارش جدید دریافت شد\n\n"

        "━━━━━━━━━━━━━━\n\n"

        f"🎫 کد پیگیری:\n"
        f"{tracking_code}\n\n"

        f"👤 آیدی مشتری:\n"
        f"{order['chat_id']}\n\n"

        f"💎 بسته:\n"
        f"{package['name']}\n\n"

        f"💰 قیمت:\n"
        f"{package['price']}\n\n"

        f"🆔 آیدی اکانت:\n"
        f"{order.get('account_id', '[ثبت نشده]')}\n\n"

        f"👤 اسم اکانت:\n"
        f"{order.get('account_name', '[ثبت نشده]')}\n\n"

        f"📧 جیمیل:\n"
        f"{order.get('gmail', '[ثبت نشده]')}\n\n"

        f"📸 اطلاعات پشتیبانی:\n"
        f"{order.get('support_info', '[ثبت نشده]')}\n\n"

        "🧾 وضعیت رسید:\n"
        "در انتظار تأیید\n\n"

        "━━━━━━━━━━━━━━"
    )


    # پیام اطلاعات سفارش

    await bot.send_message(

        ADMIN_CHAT_ID,

        admin_text
    )


    # پیام جداگانه با دکمه‌ها
    # این قسمت مهم است.

    await bot.send_message(

        ADMIN_CHAT_ID,

        "👇 عملیات رسید این سفارش:",

        chat_keypad=admin_receipt_keypad(
            tracking_code
        ),

        chat_keypad_type="New"
    )


# ==================================================
# CALLBACK دکمه‌ها
# ==================================================

@bot.on_callback()
async def all_callbacks(bot: Robot, message: Message):

    chat_id = message.chat_id


    try:

        button_id = message.aux_data.button_id

    except Exception:

        button_id = None


    if not button_id:
        return


    # ==================================================
    # دکمه‌های مدیر
    # ==================================================

    if button_id.startswith("admin_"):


        if chat_id != ADMIN_CHAT_ID:

            await message.reply(
                "❌ این بخش فقط برای مدیریت است."
            )

            return


        # ==============================================
        # تأیید رسید
        # ==============================================

        if button_id.startswith("admin_approve_"):

            tracking_code = button_id.replace(
                "admin_approve_",
                "",
                1
            )


            order = orders_by_tracking.get(
                tracking_code
            )


            if not order:

                await message.reply(
                    "❌ سفارش پیدا نشد."
                )

                return


            if order.get("status") == "completed":

                await message.reply(
                    "⚠️ این سفارش قبلاً تکمیل شده است."
                )

                return


            if order.get("status") == "processing":

                await message.reply(
                    "⚠️ این سفارش قبلاً تأیید شده است."
                )

                return


            customer_chat_id = order["chat_id"]


            order["status"] = "processing"

            order["step"] = "processing"


            # پیام به مشتری

            await bot.send_message(

                customer_chat_id,

                "✅ رسید پرداخت شما تأیید شد.\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "🔄 وضعیت سفارش شما:\n"
                "در حال انجام سفارش\n\n"

                "⏳ لطفاً تا تکمیل سفارش منتظر بمانید."
            )


            # پیام مدیر

            await message.reply(

                "✅ رسید پرداخت تأیید شد.\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "🔄 وضعیت سفارش:\n"
                "در حال انجام سفارش"
            )


            # دکمه انجام شد

            await bot.send_message(

                ADMIN_CHAT_ID,

                "🛠 سفارش آماده انجام است.\n\n"
                "بعد از انجام سفارش، دکمه زیر را بزنید:",

                chat_keypad=admin_done_keypad(
                    tracking_code
                ),

                chat_keypad_type="New"
            )

            return


        # ==============================================
        # رد رسید
        # ==============================================

        if button_id.startswith("admin_reject_"):

            tracking_code = button_id.replace(
                "admin_reject_",
                "",
                1
            )


            order = orders_by_tracking.get(
                tracking_code
            )


            if not order:

                await message.reply(
                    "❌ سفارش پیدا نشد."
                )

                return


            if order.get("status") == "completed":

                await message.reply(
                    "❌ این سفارش قبلاً تکمیل شده است."
                )

                return


            admin_reject_waiting[
                ADMIN_CHAT_ID
            ] = tracking_code


            await message.reply(

                "❌ رد رسید انتخاب شد.\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "📝 لطفاً دلیل رد شدن رسید را "
                "در پیام بعدی ارسال کنید.\n\n"

                "⚠️ پیام بعدی شما مستقیماً برای مشتری ارسال خواهد شد."
            )

            return


        # ==============================================
        # انجام شد
        # ==============================================

        if button_id.startswith("admin_done_"):

            tracking_code = button_id.replace(
                "admin_done_",
                "",
                1
            )


            order = orders_by_tracking.get(
                tracking_code
            )


            if not order:

                await message.reply(
                    "❌ سفارش پیدا نشد."
                )

                return


            if order.get("status") != "processing":

                await message.reply(

                    "❌ این سفارش هنوز در وضعیت "
                    "«در حال انجام سفارش» نیست."
                )

                return


            package = order["package"]

            customer_chat_id = order["chat_id"]


            order["status"] = "completed"

            order["step"] = "completed"


            # پیام نهایی مشتری

            await bot.send_message(

                customer_chat_id,

                "🎉 سفارش شما تکمیل شد ✅\n\n"

                f"💎 بسته:\n"
                f"{package['name']}\n\n"

                f"💰 قیمت:\n"
                f"{package['price']}\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "✅ سفارش شما با موفقیت انجام شد.\n\n"

                "ممنونم بابت انتخابتون\n"
                "𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 ❤️"
            )


            await message.reply(

                "🎉 سفارش با موفقیت تکمیل شد.\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "📦 وضعیت سفارش:\n"
                "تکمیل شده ✅"
            )

            return


        return


    # ==================================================
    # دکمه‌های مشتری
    # ==================================================

    # ==============================================
    # خرید جم
    # ==============================================

    if button_id == "buy_gem":

        await message.reply_keypad(

            "💎 انتخاب نوع خرید\n\n"
            "صفحه اول — جم با آیدی:",

            id_packages_keypad()
        )

        return


    # ==============================================
    # صفحه دوم - جم اطلاعات
    # ==============================================

    if button_id == "next_info_page":

        await message.reply_keypad(

            "💎 جم با اطلاعات\n\n"
            "یکی از بسته‌های زیر را انتخاب کنید:",

            info_packages_keypad()
        )

        return


    # ==============================================
    # برگشت صفحه اول
    # ==============================================

    if button_id == "back_id_page":

        await message.reply_keypad(

            "💎 جم با آیدی:",

            id_packages_keypad()
        )

        return


    # ==============================================
    # برگشت منوی اصلی
    # ==============================================

    if button_id == "back_main":

        await message.reply_keypad(

            "🏠 منوی اصلی:",

            main_keypad()
        )

        return


    # ==============================================
    # لغو
    # ==============================================

    if button_id == "cancel_order":

        pending_orders.pop(
            chat_id,
            None
        )

        await message.reply_keypad(

            "❌ سفارش لغو شد.\n\n"
            "🏠 به منوی اصلی برگشتید.",

            main_keypad()
        )

        return


    # ==============================================
    # پیگیری سفارش
    # ==============================================

    if button_id == "track_order":

        order = pending_orders.get(chat_id)


        if not order:

            await message.reply(
                "❌ در حال حاضر سفارشی برای شما پیدا نشد."
            )

            return


        tracking_code = order.get(
            "tracking_code",
            "هنوز ثبت نشده"
        )


        package = order.get(
            "package",
            {}
        )


        status = order.get(
            "status",
            "collecting_info"
        )


        status_text = {

            "collecting_info":
                "⏳ در حال تکمیل اطلاعات",

            "waiting_receipt":
                "⏳ در انتظار ارسال رسید",

            "waiting_confirmation":
                "⏳ در انتظار تأیید رسید",

            "rejected":
                "❌ رسید رد شده",

            "processing":
                "🔄 در حال انجام سفارش",

            "completed":
                "✅ تکمیل شده"

        }.get(

            status,

            "⏳ در حال تکمیل اطلاعات"
        )


        await message.reply(

            "🎫 پیگیری سفارش\n\n"

            "━━━━━━━━━━━━━━\n\n"

            f"🎫 کد پیگیری:\n"
            f"{tracking_code}\n\n"

            f"💎 بسته:\n"
            f"{package.get('name', 'ثبت نشده')}\n\n"

            f"💰 قیمت:\n"
            f"{package.get('price', 'ثبت نشده')}\n\n"

            f"📦 وضعیت:\n"
            f"{status_text}\n\n"

            "━━━━━━━━━━━━━━"
        )

        return


    # ==============================================
    # پشتیبانی
    # ==============================================

    if button_id == "support":

        await message.reply(

            "🆘 پشتیبانی TRIX SHOP\n\n"

            "برای پشتیبانی با مدیریت ارتباط بگیرید."
        )

        return


    # ==============================================
    # بسته‌های جم با آیدی
    # ==============================================

    if button_id.startswith("buy_id_"):

        package_id = button_id.replace(
            "buy_",
            "",
            1
        )


        package = PACKAGES.get(package_id)


        if not package:

            await message.reply(
                "❌ بسته پیدا نشد."
            )

            return


        pending_orders[chat_id] = {

            "chat_id": chat_id,

            "package": package,

            "step": "account_id",

            "status": "collecting_info"
        }


        await message.reply_keypad(

            "💎 بسته انتخابی:\n"
            f"{package['name']}\n\n"

            "💰 قیمت:\n"
            f"{package['price']}\n\n"

            "برای ادامه روی «تأیید سفارش» بزنید.",

            order_keypad(package_id)
        )

        return


    # ==============================================
    # بسته‌های جم با اطلاعات
    # ==============================================

    if button_id.startswith("buy_info_"):

        package_id = button_id.replace(
            "buy_",
            "",
            1
        )


        package = PACKAGES.get(package_id)


        if not package:

            await message.reply(
                "❌ بسته پیدا نشد."
            )

            return


        pending_orders[chat_id] = {

            "chat_id": chat_id,

            "package": package,

            "step": "confirm_info",

            "status": "collecting_info"
        }


        await message.reply_keypad(

            "💎 بسته انتخابی:\n"
            f"{package['name']}\n\n"

            "💰 قیمت:\n"
            f"{package['price']}\n\n"

            "برای ادامه روی «تأیید سفارش» بزنید.",

            order_keypad(package_id)
        )

        return


    # ==============================================
    # تأیید سفارش
    # ==============================================

    if button_id.startswith("confirm_"):

        package_id = button_id.replace(
            "confirm_",
            "",
            1
        )


        package = PACKAGES.get(package_id)


        if not package:

            await message.reply(
                "❌ بسته پیدا نشد."
            )

            return


        pending_orders[chat_id] = {

            **pending_orders.get(chat_id, {}),

            "chat_id": chat_id,

            "package": package,

            "status": "collecting_info"
        }


        order = pending_orders[chat_id]


        # ==========================================
        # جم با آیدی
        # ==========================================

        if package["type"] == "id":

            order["step"] = "account_id"


            await message.reply(

                "🆔 لطفاً آیدی اکانت را ارسال کنید:"
            )

            return


        # ==========================================
        # جم با اطلاعات
        # ==========================================

        if package["type"] == "info":

            order["step"] = "gmail"


            await message.reply(

                "سفارش شما تایید شد ✅\n\n"

                "💎 نوع سفارش:\n"
                f"{package['name']}\n\n"

                "💰 قیمت:\n"
                f"{package['price']}\n\n"

                "📧 جی‌میل:\n"
                "[ ]\n\n"

                "🗳️ رمز جیمیل:\n"
                "[ ]\n\n"

                "📸 شات 10 تایی پشتیبانی:\n"
                "[ ]\n\n"

                "👤 اسم اکانت:\n"
                "[ ]\n\n"

                "🆔 ایدی اکانت:\n"
                "[ ]\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "📧 لطفاً فقط آدرس جی‌میل ، رمز ، کد بک اپ 10 تایی ، ایدی و اسم اکانت را ارسال کنید.\n"
                "⚠️ جیمیل ، رمز ، شات کامل کد پشتیبانی ، ایدی اکانت و اسم اکانت را یکجا و همزمان ارسال کنید ."
            )

            return


# ==================================================
# اجرای ربات
# ==================================================

print("================================")
print("TRIX SHOP BOT STARTED")
print("================================")

bot.run()
