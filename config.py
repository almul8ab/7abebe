import os
from os import getenv
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()
admins = {}
SESSION_NAME = getenv("SESSION_NAME")
BOT_TOKEN = getenv("BOT_TOKEN")
BOT_NAME = getenv("BOT_NAME", "𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧")
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
OWNER_NAME = getenv("OWNER_NAME")
ALIVE_NAME = getenv("ALIVE_NAME")
BOT_USERNAME = getenv("BOT_USERNAME")
ASSISTANT_NAME = getenv("ASSISTANT_NAME")
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "JepthonSupport")
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "Jepthon")
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "1047777673").split()))
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! .").split())
ALIVE_IMG = getenv("ALIVE_IMG", "https://telegra.ph/file/440d26335ffda1f74e12d.jpg")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "60"))
UPSTREAM_REPO = getenv("UPSTREAM_REPO")
IMG_1 = getenv("IMG_1", "https://telegra.ph/file/440d26335ffda1f74e12d.jpg")
IMG_2 = getenv("IMG_2", "https://telegra.ph/file/440d26335ffda1f74e12d.jpg")
IMG_3 = getenv("IMG_3", "https://telegra.ph/file/440d26335ffda1f74e12d.jpg")
