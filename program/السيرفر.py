# Copyright (C) 2021 Veez Project

import re
import uuid
import socket

import psutil
import platform
from driver.filters import command2
from pyrogram import Client, filters
from driver.decorators import sudo_users_only, humanbytes


# FETCH SYSINFO

@Client.on_message(command2(["النظام","السيرفر","معلومات السيرفر"]))
@sudo_users_only
async def give_sysinfo(client, message):
    splatform = platform.system()
    platform_release = platform.release()
    platform_version = platform.version()
    architecture = platform.machine()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    processor = platform.processor()
    ram = humanbytes(round(psutil.virtual_memory().total))
    cpu_freq = psutil.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
    else:
        cpu_freq = f"{round(cpu_freq, 2)}MHz"
    du = psutil.disk_usage(client.workdir)
    psutil.disk_io_counters()
    disk = f"{humanbytes(du.used)} / {humanbytes(du.total)} " f"({du.percent}%)"
    cpu_len = len(psutil.Process().cpu_affinity())
    somsg = f"""🖥 **معلومات السيرفر**
    
**النظام :** `{splatform}`
**الاصدار :** `{platform_release}`
**النسخة :** `{platform_version}`
**المعمار :** `{architecture}`
**اسم المضيف :** `{hostname}`
**ايبي :** `{ip_address}`
**ماك :** `{mac_address}`
**البروسيسور :** `{processor}`
**الرام : ** `{ram}`
**المعالج :** `{cpu_len}`
**تردد المعالج :** `{cpu_freq}`
**التخزين :** `{disk}`
"""
    await message.reply(somsg)
