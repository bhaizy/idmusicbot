import time
import platform
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_NAME, BOT_VERSION, DEFAULT_THUMB_URL
from utils.db import db

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

START_TIME = time.time()


def get_uptime() -> str:
    """Bot ka uptime calculate karo."""
    uptime_seconds = int(time.time() - START_TIME)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


@Client.on_message(filters.command("stats", prefixes=".") & filters.me)
async def stats_command(client: Client, message: Message):
    """📊 .stats — Bot statistics"""
    stats = db.get_stats()
    uptime = get_uptime()

    text = (
        f"[​]({DEFAULT_THUMB_URL})"
        f"📊 **{BOT_NAME} Stats**\n\n"
        f"👤 Users: `{stats['users']}`\n"
        f"👥 Groups: `{stats['groups']}`\n"
        f"🎵 Songs Played: `{stats['songs_played']}`\n"
        f"⏱ Uptime: `{uptime}`\n"
        f"📦 Version: `{BOT_VERSION}`\n"
    )

    if PSUTIL_AVAILABLE:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        text += (
            f"\n💻 **System**\n"
            f"🔲 CPU: `{cpu}%`\n"
            f"💾 RAM: `{ram.percent}%` ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)\n"
            f"🖥 OS: `{platform.system()} {platform.release()}`\n"
        )

    text += f"\n🕐 Started: `{stats.get('started_at', 'Unknown')}`"

    await message.edit_text(text)
