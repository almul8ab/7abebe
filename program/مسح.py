# Copyright (C) 2021 By VeezMusicProject

import os
from pyrogram import Client, filters
from pyrogram.types import Message
from driver.filters import command2
from driver.decorators import sudo_users_only, errors

downloads = os.path.realpath("program/downloads")
raw = os.path.realpath(".")

@Client.on_message(command2(["حذف المحمل"]))
@errors
@sudo_users_only
async def clear_downloads(_, message: Message):
    ls_dir = os.listdir(downloads)
    if ls_dir:
        for file in os.listdir(downloads):
            os.remove(os.path.join(downloads, file))
        await message.reply_text("✅ **تم حذف جميع الملفات المحملة**")
    else:
        await message.reply_text("❌ **لا يوجد ملفات محملة**")

        
@Client.on_message(command2(["حذف الكل"]))
@errors
@sudo_users_only
async def clear_raw(_, message: Message):
    ls_dir = os.listdir(raw)
    if ls_dir:
        for file in os.listdir(raw):
            if file.endswith('.raw'):
                os.remove(os.path.join(raw, file))
        await message.reply_text("✅ **تم حذف جميع الملفات**")
    else:
        await message.reply_text("❌ **لا يوجد ملفات لمسحها**")


@Client.on_message(command2(["مسح الكل"]))
@errors
@sudo_users_only
async def cleanup(_, message: Message):
    pth = os.path.realpath(".")
    ls_dir = os.listdir(pth)
    if ls_dir:
        for dta in os.listdir(pth):
            os.system("rm -rf *.raw *.jpg *.png")
        await message.reply_text("✅ **تم المسح**")
    else:
        await message.reply_text("✅ **بالتأكيد تم مسحها**")
