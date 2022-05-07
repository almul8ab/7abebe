import asyncio
from config import BOT_USERNAME, SUDO_USERS, ASSISTANT_NAME
from driver.decorators import authorized_users_only, sudo_users_only, errors
from driver.filters import command, other_filters
from driver.veez import user as USER
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant


@Client.on_message(
    command(["userbotjoin", f"userbotjoin@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot
)
@authorized_users_only
@errors
async def join_group(client, message):
    chid = message.chat.id
    try:
        invitelink = await client.export_chat_invite_link(chid)
    except BaseException:
        await message.reply_text(
            "• **ليس لدي صلاحيه:**\n\n» ❌ __إضافة مستخدمين__",
        )
        return

    try:
        await USER.join_chat(invitelink)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        print(e)
        await message.reply_text(
            f"🛑 حدث خطأ 🛑 \n\n**البوت المساعد لم يستطع الدخول لكثرة الطلبات**"
            "\n\n**حاول مرة اخري او قم بإضافته يدويا**\n\nيمكنك ارسال اي رساله للحساب المساعد وسيقوم باضافتك لجهات الاتصال"
            f"\nمعرف الحساب المساعد @{ASSISTANT_NAME}",
            )
        return
    await message.reply_text(
        f"✅ **تم دخول الحساب المساعد بنجاح**",
    )


@Client.on_message(command(["userbotleave",
                            f"leave@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def leave_one(client, message):
    try:
        await USER.send_message(message.chat.id, "✅ قام البوت المساعد بالخروج من المحادثة")
        await USER.leave_chat(message.chat.id)
    except BaseException:
        await message.reply_text(
            "❌ **لن يستطيع البوت المساعد الخروج لكثرة الطلبات.**\n\n**» برجاء طرده يدويا**"
        )

        return


@Client.on_message(command(["leaveall", f"leaveall@{BOT_USERNAME}"]))
@sudo_users_only
async def leave_all(client, message):
    if message.from_user.id not in SUDO_USERS:
        return

    left = 0
    failed = 0
    lol = await message.reply("🔄 **سوف يغادر الحساب المساعد من المجموعات**!")
    async for dialog in USER.iter_dialogs():
        try:
            await USER.leave_chat(dialog.chat.id)
            left += 1
            await lol.edit(
                f"الحساب المساعد يغادر جميع المجموعات...\n\nخرج من: {left} مجموعه.\nفشل مغادرة : {failed} مجموعه."
            )
        except BaseException:
            failed += 1
            await lol.edit(
                f"الحساب المساعد يغادر جميع المجموعات...\n\nخرج من: {left} مجموعه.\nفشل مغادرة : {failed} مجموعه."
            )
    await client.send_message(
        message.chat.id, f"✅ تم الخروج من: {left} مجموعه.\n❌ فشل: {failed} مجموعه."
    )
