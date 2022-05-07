# Copyright (C) 2021 By Veez Music-Project
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

import asyncio
import re

from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch


def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1)
        for r in search.result()["result"]:
            ytid = r["id"]
            if len(r["title"]) > 34:
                songname = r["title"][:70]
            else:
                songname = r["title"]
            url = f"https://www.youtube.com/watch?v={ytid}"
        return [songname, url]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command(["mplay","play", f"mplay@{BOT_USERNAME}"]) & other_filters)
async def play(c: Client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="• القائمة", callback_data="cbmenu"),
                InlineKeyboardButton(text="• اغلاق", callback_data="cls"),
            ]
        ]
    )
    if m.sender_chat:
        return await m.reply_text("انت مسؤول مجهول\n\n» قم بي الغاء خاصية التخفي")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"خطأ:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 لاستخدامي يجب ان اكون **مسؤول** مع **الصلاحيات** التالية:\n\n» ❌ __حذف الرسائل__\n» ❌ __حظر المستخدمين__\n» ❌ __دعوة المستخدمين__\n» ❌ __التحكم في المحادثات الصوتية__"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "قم بي اعطائي الصلاحية التالية:" + "\n\n» ❌ __التحكم في المحادثات الصوتية__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "قم بي اعطائي الصلاحية التالية:" + "\n\n» ❌ __حذف الرسائل__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("قم بي اعطائي الصلاحية التالية:" + "\n\n» ❌ __دعوة المستخدمين__")
        return
    if not a.can_restrict_members:
        await m.reply_text("قم بي اعطائي الصلاحية التالية:" + "\n\n» ❌ __حظر المستخدمين__")
        return
    try:
        ubot = await user.get_me()
        b = await c.get_chat_member(chat_id, ubot.id)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} محظور في المجموعة {m.chat.title}\n\n» قم بي الغاء حظره و اضافتة الي المجموعة"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **الحساب المساعد فشل في الانضمام**\n\n**الخطأ**: `{e}`")
                return
        else:
            try:
                pope = await c.export_chat_invite_link(chat_id)
                pepo = await c.revoke_chat_invite_link(chat_id, pope)
                await user.join_chat(pepo.invite_link)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **الحساب المساعد فشل في الانضمام**\n\n**الخطأ**: `{e}`"
                )

    if replied:
        if replied.audio or replied.voice:
            suhu = await replied.reply("📥 **تحميل الصوت...**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:70]
                else:
                    if replied.audio.file_name:
                        songname = replied.audio.file_name[:70]
                    else:
                        songname = "Audio"
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **تم اضافتها الي قائمة التشغيل الدور »** `{pos}`\n\n🏷 **الاسم:** [{songname}]({link})\n💭 **المحادثة:** `{chat_id}`\n🎧 **مطلوبة بوسطة:** {m.from_user.mention()}",
                    reply_markup=keyboard,
                )
            else:
             try:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_2}",
                    caption=f"💡 **تم تشغيل الموسيقي.**\n\n🏷 **الاسم:** [{songname}]({link})\n💭 **المحادثة:** `{chat_id}`\n💡 **الحالة:** يعمل\n🎧 **مطلوبة بوسطة:** {requester}",
                    reply_markup=keyboard,
                )
             except Exception as e:
                await suhu.delete()
                await m.reply_text(f"🚫 خطأ:\n\n» `{e}`")
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» قم بي الرد علي ملف صوتي او اعطائي شيئ للبحث"
                )
            else:
                suhu = await m.reply("🔎 **جاري البحث...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("❌ لم اجد نتائج")
                else:
                    songname = search[0]
                    url = search[1]
                    veez, ytlink = await ytdl(url)
                    if veez == 0:
                        await suhu.edit(f"❌ خطأ في مكاتب السورس\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Audio", 0
                            )
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_1}",
                                caption=f"💡 **تم اضافتها الي قائمة التشغيل الدور »** `{pos}`\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثة:** `{chat_id}`\n🎧 **مطلوبة بوسطة:** {requester}",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                await suhu.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=f"{IMG_2}",
                                    caption=f"💡 **تم تشغيل الموسيقي.**\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثة:** `{chat_id}`\n💡 **الحالة:** يعمل\n🎧 **مطلوبة بوسطة:** {requester}",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await suhu.delete()
                                await m.reply_text(f"🚫 خطأ: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "» قم بي الرد علي ملف صوتي او اعطائي شيئ للبحث"
            )
        else:
            suhu = await m.reply("🔎 **جاري البحث...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("❌ لم اجد اي نتائج")
            else:
                songname = search[0]
                url = search[1]
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await suhu.edit(f"❌ خطأ في مكاتب السورس\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await suhu.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=f"{IMG_1}",
                            caption=f"💡 **تم اضافتها الي قائمة التشغيل الدور »** `{pos}`\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثة:** `{chat_id}`\n🎧 **مطلوبة بوسطة:** {requester}",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_2}",
                                caption=f"💡 **تم تشغيل الموسيقي.**\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثة:** `{chat_id}`\n💡 **الحالة:** يعمل\n🎧 **مطلوبة بوسطة:** {requester}",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await suhu.delete()
                            await m.reply_text(f"🚫 خطأ: `{ep}`")

