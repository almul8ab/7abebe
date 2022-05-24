from datetime import datetime
from sys import version_info
from time import time
from driver.veez import user as USER
from config import (
    ALIVE_IMG,
    ASSISTANT_NAME,
    ALIVE_NAME,
    BOT_NAME,
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_NAME,
    UPDATES_CHANNEL,
)
from program import __version__
from driver.filters import command, other_filters
from pyrogram import Client, filters
from pyrogram import __version__ as pyrover
from pytgcalls import (__version__ as pytover)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

__major__ = 0
__minor__ = 2
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("اسبوع", 60 * 60 * 24 * 7),
    ("يوم", 60 * 60 * 24),
    ("ساعة", 60 * 60),
    ("دقيقة", 60),
    ("ثانيا", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else ""))
    return ", ".join(parts)


@Client.on_message(command(["start"]) & filters.private & ~filters.edited)
async def start_(client: Client, message: Message):
    await message.reply_text(
        f"""✨ **مرحبا {message.from_user.mention()} !**\n
💭 [{BOT_NAME}](https://t.me/{BOT_USERNAME}) **انا بوت استطيع تشغيل الموسيقى والفيديو في محادثتك الصوتية
💡 **تعلم طريقة تشغيلي واوامر التحكم بي عن طريق  » 📚 الاوامر !**

🔖 **لتعلم طريقة تشغيلي بمجموعتك اضغط علي » ❓اوامر اساسيه **
تم اضافتك الي جهات الاتصال في الحساب المساعد @{ASSISTANT_NAME}""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ أضفني لمجموعتك ➕",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                    )
                ],
                [InlineKeyboardButton("❓ الاوامر الاساسيه", callback_data="cbhowtouse")],
                [
                    InlineKeyboardButton("📚 الاوامر", callback_data="cbcmds"),
                    InlineKeyboardButton("❤️ المطور", url=f"https://t.me/{OWNER_NAME}"),
                ],
                [
                    InlineKeyboardButton(
                        "👥 كروب الدعم", url=f"https://t.me/{GROUP_SUPPORT}"
                    ),
                    InlineKeyboardButton(
                        "↬ 𝙹𝙴𝙿𝚃𝙷𝙾𝙽 𝙰𝚁𝙰𝙱 ⟊", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ],
            ]
        ),
        disable_web_page_preview=True,
    )
    await USER.add_contact(message.from_user.id, "جيبثون العرب")


@Client.on_message(
    command(["alive", f"alive@{BOT_USERNAME}"]) & ~filters.edited
)
async def alive(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✨ كروب الدعم", url=f"https://t.me/{GROUP_SUPPORT}"),
                InlineKeyboardButton(
                    "↬ 𝙹𝙴𝙿𝚃𝙷𝙾𝙽 𝙰𝚁𝙰𝙱 ⟊", url=f"https://t.me/{UPDATES_CHANNEL}"
                ),
            ]
        ]
    )

    alive = f"""**أنا {BOT_NAME}**
✨ أعمل الأن بشكل طبيعي
🍀 مطوري : [{ALIVE_NAME}](https://t.me/{OWNER_NAME})
✨ إصداري: {__version__}
🍀 إصدار البايوجرام: {pyrover}
✨ إصدار البايثون: {__python_version__}
🍀 إصدار المحادثة الصوتيه: {pytover.__version__}
✨ وقت البدء: {uptime}

**شكرا لإضافتي لتشغيل الموسيقي والفديو في محادثتك الصوتية** ❤"""

    await message.reply_photo(
        photo=f"{ALIVE_IMG}",
        caption=alive,
        reply_markup=keyboard,
    )


@Client.on_message(command(["ping", f"ping@{BOT_USERNAME}"]) & ~filters.edited)
async def ping_pong(client: Client, message: Message):
    start = time()
    m_reply = await message.reply_text("جاري قياس البينك...")
    delta_ping = time() - start
    await m_reply.edit_text("🏓 بينج\n" f"⚡️ `{delta_ping * 1000:.3f} ms`")


@Client.on_message(command(["uptime", f"uptime@{BOT_USERNAME}"]) & ~filters.edited)
async def get_uptime(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        "🤖 حاله البوت:\n"
        f"• **وقت التشغيل:** `{uptime}`\n"
        f"• **وقت البدء:** `{START_TIME_ISO}`"
    )
