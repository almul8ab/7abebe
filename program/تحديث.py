import os
import sys

from git import Repo
from pyrogram.types import Message
from driver.filters import command2
from pyrogram import Client, filters
from os import system, execle, environ
from driver.decorators import sudo_users_only
from git.exc import InvalidGitRepositoryError
from config import UPSTREAM_REPO


def gen_chlog(repo, diff):
    upstream_repo_url = Repo().remotes[0].config_reader.get("url").replace(".git", "")
    ac_br = repo.active_branch.name
    ch_log = tldr_log = ""
    ch = f"<b>updates for <a href={upstream_repo_url}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    ch_tl = f"updates for {ac_br}:"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"\n\n💬 <b>{c.count()}</b> 🗓 <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b>"
            f"<a href={upstream_repo_url.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> 👨‍💻 <code>{c.author}</code>"
        )
        tldr_log += f"\n\n💬 {c.count()} 🗓 [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] 👨‍💻 {c.author}"
    if ch_log:
        return str(ch + ch_log), str(ch_tl + tldr_log)
    return ch_log, tldr_log


def updater():
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    ac_br = repo.active_branch.name
    if "upstream" in repo.remotes:
        ups_rem = repo.remote("upstream")
    else:
        ups_rem = repo.create_remote("upstream", UPSTREAM_REPO)
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    return bool(changelog)


@Client.on_message(command2(["تحديث"]))
@sudo_users_only
async def update_repo(_, message: Message):
    chat_id = message.chat.id
    msg = await message.reply("🔄 جاري التحديث...")
    update_avail = updater()
    if update_avail:
        await msg.edit("✅ تم التحديث\n\n• تم اعاده تشغيل البوت , سيتم التفعيل بعد دقيقه.")
        system("git pull -f && pip3 install -r requirements.txt")
        execle(sys.executable, sys.executable, "main.py", environ)
        return
    await msg.edit("البوت **تم نحديثه**", disable_web_page_preview=True)


@Client.on_message(command2(["اعادة تشغيل","اعاده تشغيل","اعادة التشغيل","اعاده التشغيل"]) & ~filters.edited)
@sudo_users_only
async def restart_bot(_, message: Message):
    msg = await message.reply("جاري اعادة تشغيل البوت...")
    args = [sys.executable, "main.py"]
    await msg.edit("✅ تم اعادة تشغيل البوت\n\n• الان يمكنك استخدام البوت.")
    execle(sys.executable, *args, environ)
    return
