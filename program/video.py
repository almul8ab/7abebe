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
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
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
        "best[height<=?360][width<=?720]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command(["vplay", f"vplay@{BOT_USERNAME}"]) & other_filters)
async def vplay(c: Client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="• القائمة", callback_data="cbmenu"),
                InlineKeyboardButton(text="• اغلاق ", callback_data="cls"),
            ]
        ]
    )
    if m.sender_chat:
        return await m.reply_text("انت مسؤول مجهول !\n\n» قم بإلغاء خاصية التخفي.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"خطأ:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 لاستخدامي يجب عليك اعطائي تلك الصلاحيات:\n\n» ❌ __حذف الرسائل__\n» ❌ __حظر المستخدمين__\n» ❌ __إضافة اعضاء__\n» ❌ __إدارة المحادثة الصوتية__\n\nيتم تحديث البيانات تلقائيًا بعد ترقيتي واعطائي الصلاحيات"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "لم تعطني صلاحية" + "\n\n» ❌ __إداره المحادثة الصوتية__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "لم تعطني صلاحية:" + "\n\n» ❌ __مسح الرسائل__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("لم تعطني صلاحية:" + "\n\n» ❌ __اضافه الاعضاء__")
        return
    if not a.can_restrict_members:
        await m.reply_text("لم تعطني صلاحية:" + "\n\n» ❌ __حظر مستخدمين__")
        return
    try:
        ubot = await user.get_me()
        b = await c.get_chat_member(chat_id, ubot.id)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **محظور من المجموعة** {m.chat.title}\n\n» **قم بفك حظر البوت المساعد اولا.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **البوت المساع فشل في الدخول**\n\n**السبب**: `{e}`")
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
                    f"❌ **فشل البوت المساعد في الدخول**\n\n**السبب**: `{e}`"
                )

    if replied:
        if replied.video or replied.document:
            loser = await replied.reply("📥 **يتم تحميل الفديو...**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await loser.edit(
                        "» __فقط 720, 480, 360 المصرح بها__ \n💡 ** الان يتم عرض الفديو بدقة 720**"
                    )
            try:
                if replied.video:
                    songname = replied.video.file_name[:70]
                elif replied.document:
                    songname = replied.document.file_name[:70]
            except BaseException:
                songname = "Video"

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **تم إضافته لقائمة الانتظار »** `{pos}`\n\n🏷 **الاسم:** [{songname}]({link})\n💭 **المحادثه:** `{chat_id}`\n🎧 **مطلوب بواسطة:** {requester}",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        dl,
                        HighQualityAudio(),
                        amaze,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_2}",
                    caption=f"💡 **تم بدء عرض الفديو.**\n\n🏷 **الاسم:** [{songname}]({link})\n💭 **المحادثه:** `{chat_id}`\n💡 الحالة : مشِغل\n🎧 **مطلوبة بواسطه:** {requester}",
                    reply_markup=keyboard,
                )
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» قم بالرد علي ملف فديو او اعطيني اسم فديو لتشغيله"
                )
            else:
                loser = await m.reply("🔎 **جاري البحث...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                Q = 720
                amaze = HighQualityVideo()
                if search == 0:
                    await loser.edit("❌ **لا يوجد نتائج.**")
                else:
                    songname = search[0]
                    url = search[1]
                    veez, ytlink = await ytdl(url)
                    if veez == 0:
                        await loser.edit(f"❌ يوجد خطأ في المكتبه\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Video", Q
                            )
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_1}",
                                caption=f"💡 **تم الوضع  في قائمة الانتظار »** `{pos}`\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثة:** `{chat_id}`\n🎧 **مطلوب بواسطة:** {requester}",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioVideoPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                        amaze,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                                await loser.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=f"{IMG_2}",
                                    caption=f"💡 **تم بدء العرض.**\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثة:** `{chat_id}`\n💡 **الحاله:** `Playing`\n🎧 **مطلوب بواسطه** {requester}",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await loser.delete()
                                await m.reply_text(f"🚫 خطأ: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "» قم بالرد علي ملف فديو او اعطيني اسم فديو لتشغيله**"
            )
        else:
            loser = await m.reply("🔎 **جاي البحث...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            amaze = HighQualityVideo()
            if search == 0:
                await loser.edit("❌ **لا يوجد نتائج.**")
            else:
                songname = search[0]
                url = search[1]
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await loser.edit(f"❌ يوجد خطأ بالمكتبه\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await loser.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=f"{IMG_1}",
                            caption=f"💡 **تمت الإضافة لقائمة الانتظار »** `{pos}`\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثه:** `{chat_id}`\n🎧 **مطلوب بواسطه:** {requester}",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioVideoPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                    amaze,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_2}",
                                caption=f"💡 **تم بدء العرض.**\n\n🏷 **الاسم:** [{songname}]({url})\n💭 **المحادثة:** `{chat_id}`\n💡 الحالة : مشِغل\n🎧 **مطلوب بواسطة:** {requester}",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await loser.delete()
                            await m.reply_text(f"🚫 خطأ: `{ep}`")


@Client.on_message(command(["vstream", f"vstream@{BOT_USERNAME}"]) & other_filters)
async def vstream(c: Client, m: Message):
    m.reply_to_message
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
        return await m.reply_text("انت مسؤول مجهول !\n\n» قم بإلغاء صلاحية التخفي.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"خطأ:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 لاستخدامي يجب عليك اعطائي تلك الصلاحيات:\n\n» ❌ __حذف الرسائل__\n» ❌ __حظر المستخدمين__\n» ❌ __إضافة اعضاء__\n» ❌ __إدارة المحادثة الصوتية__\n\nيتم تحديث البيانات تلقائيًا بعد ترقيتي واعطائي الصلاحيات"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "لم تعطني صلاحية:" + "\n\n» ❌ __إداره المحادثة الصوتية__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "لم تعطني صلاحية:" + "\n\n» ❌ __مسح الرسائل__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("لم تعطني صلاحية:" + "\n\n» ❌ __إضافه أعضاء__")
        return
    if not a.can_restrict_members:
        await m.reply_text("لم تعطني صلاحية:" + "\n\n» ❌ __حظر المستخدمين__")
        return
    try:
        ubot = await user.get_me()
        b = await c.get_chat_member(chat_id, ubot.id)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **محظور من المجموعة** {m.chat.title}\n\n» **قم بإلغاء حظره من المجموعة.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **لم يستطع البوت المساعد الدخول**\n\n**السبب**: `{e}`")
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
                    f"❌ **البوت المساعد لم يستطع الانضمام**\n\n**السبب**: `{e}`"
                )

    if len(m.command) < 2:
        await m.reply("» اعطني رابط للعرض لايف")
    else:
        if len(m.command) == 2:
            link = m.text.split(None, 1)[1]
            Q = 720
            loser = await m.reply("🔄 **يتم التقدم...**")
        elif len(m.command) == 3:
            op = m.text.split(None, 1)[1]
            link = op.split(None, 1)[0]
            quality = op.split(None, 1)[1]
            if quality == "720" or "480" or "360":
                Q = int(quality)
            else:
                Q = 720
                await m.reply(
                    "» غير مصرح لي بجودة اعلي من 720"
                )
            loser = await m.reply("🔄 **جاري التقدم...**")
        else:
            await m.reply("**/vstream {link} {720/480/360}**")

        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, link)
        if match:
            veez, livelink = await ytdl(link)
        else:
            livelink = link
            veez = 1

        if veez == 0:
            await loser.edit(f"❌ يوجد خطأ بالمكتبة\n\n» `{ytlink}`")
        else:
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **تم الإضافة لقائمة الانتظار »** `{pos}`\n\n💭 **المحادثة:** `{chat_id}`\n🎧 **مطلوب بواسطة:** {requester}",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                try:
                    await call_py.join_group_call(
                        chat_id,
                        AudioVideoPiped(
                            livelink,
                            HighQualityAudio(),
                            amaze,
                        ),
                        stream_type=StreamType().live_stream,
                    )
                    add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                    await loser.delete()
                    requester = (
                        f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    )
                    await m.reply_photo(
                        photo=f"{IMG_2}",
                        caption=f"💡 **[البث الحي]({link}) يتم عرضه.**\n\n💭 **المحادثة:** `{chat_id}`\n💡 الحالة : مشِغل  \n🎧 **مطلوب بواسطة:** {requester}",
                        reply_markup=keyboard,
                    )
                except Exception as ep:
                    await loser.delete()
                    await m.reply_text(f"🚫 خطأ: `{ep}`")
