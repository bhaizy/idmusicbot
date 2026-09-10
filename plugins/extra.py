# Cobra — Extra Commands
# MusicBoTOp se inspired + nayi commands

import os
import time
import shutil
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.youtube import YouTube, download_song, download_video
from utils.db import db
from config import DOWNLOADS_DIR, OWNER_ID, DEFAULT_THUMB_URL


@Client.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_command(client: Client, message: Message):
    """🏓 .ping — Bot alive check + response time"""
    start = time.time()
    msg = await message.edit_text("🏓 **Pinging...**")
    end = time.time()
    ping_ms = round((end - start) * 1000, 2)
    await msg.edit_text(
        f"[​]({DEFAULT_THUMB_URL})"
        f"🏓 **Pong!**\n\n"
        f"⚡ Response: `{ping_ms}ms`\n"
        f"🤖 **Cobra** is alive and running!"
    )


@Client.on_message(filters.command("song", prefixes=".") & filters.me)
async def song_command(client: Client, message: Message):
    """🎵 .song <query/link> — Audio file download karke chat mein send karo"""
    query = " ".join(message.command[1:]) if len(message.command) > 1 else None

    if not query:
        await message.edit_text("❌ **Song name ya link do!**\n\nUsage: `.song <name/link>`")
        return

    status = await message.edit_text(f"🔍 **Searching...** `{query}`")

    # Search karo
    is_yt = await YouTube.is_youtube_link(query)
    if is_yt:
        video_id = YouTube.extract_video_id(query)
        details = await YouTube.details(video_id, videoid=True) if video_id else None
    else:
        details = await YouTube.search(query)

    if not details:
        await status.edit_text("❌ **Kuch nahi mila!**")
        return

    title = details["title"]
    vidid = details["vidid"]
    duration = details.get("duration", "Unknown")
    thumb = details.get("thumbnail", "")

    await status.edit_text(f"📥 **Downloading...** `{title}`")

    # Audio download
    file_path = await download_song(vidid)
    if not file_path:
        await status.edit_text("❌ **Download fail!** Try again.")
        return

    await status.edit_text(f"📤 **Uploading...** `{title}`")

    # Thumbnail download
    thumb_path = None
    if thumb:
        try:
            thumb_path = os.path.join(DOWNLOADS_DIR, f"{vidid}_thumb.jpg")
            async with aiohttp.ClientSession() as session:
                async with session.get(thumb) as resp:
                    if resp.status == 200:
                        with open(thumb_path, "wb") as f:
                            f.write(await resp.read())
        except Exception:
            thumb_path = None

    try:
        await message.reply_audio(
            audio=file_path,
            title=title,
            duration=0,
            thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
            caption=f"🎵 **{title}**\n⏱ Duration: `{duration}`\n\n📥 Downloaded by **Cobra**",
        )
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ **Upload fail:** `{e}`")

    # Cleanup thumbnail
    if thumb_path and os.path.exists(thumb_path):
        try:
            os.remove(thumb_path)
        except Exception:
            pass

    # Track stats
    db.increment_songs()


@Client.on_message(filters.command("vsong", prefixes=".") & filters.me)
async def vsong_command(client: Client, message: Message):
    """🎬 .vsong <query/link> — Video download karke chat mein send karo"""
    query = " ".join(message.command[1:]) if len(message.command) > 1 else None

    if not query:
        await message.edit_text("❌ **Video name ya link do!**\n\nUsage: `.vsong <name/link>`")
        return

    status = await message.edit_text(f"🔍 **Searching...** `{query}`")

    is_yt = await YouTube.is_youtube_link(query)
    if is_yt:
        video_id = YouTube.extract_video_id(query)
        details = await YouTube.details(video_id, videoid=True) if video_id else None
    else:
        details = await YouTube.search(query)

    if not details:
        await status.edit_text("❌ **Kuch nahi mila!**")
        return

    title = details["title"]
    vidid = details["vidid"]
    duration = details.get("duration", "Unknown")

    await status.edit_text(f"📥 **Downloading video...** `{title}`")

    file_path = await download_video(vidid)
    if not file_path:
        await status.edit_text("❌ **Video download fail!** Try again.")
        return

    await status.edit_text(f"📤 **Uploading video...** `{title}`")

    try:
        await message.reply_video(
            video=file_path,
            caption=f"🎬 **{title}**\n⏱ Duration: `{duration}`\n\n📥 Downloaded by **Cobra**",
            supports_streaming=True,
        )
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ **Upload fail:** `{e}`")

    db.increment_songs()


@Client.on_message(filters.command("lyrics", prefixes=".") & filters.me)
async def lyrics_command(client: Client, message: Message):
    """📝 .lyrics <song name> — Song ke lyrics fetch karo"""
    query = " ".join(message.command[1:]) if len(message.command) > 1 else None

    if not query:
        await message.edit_text("❌ **Song name do!**\n\nUsage: `.lyrics <song name>`")
        return

    status = await message.edit_text(f"🔍 **Searching lyrics...** `{query}`")

    try:
        async with aiohttp.ClientSession() as session:
            # Lyrics API use karte hain
            url = f"https://some-random-api.com/others/lyrics?title={query}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    await status.edit_text("❌ **Lyrics nahi mile!** Try different song name.")
                    return
                data = await resp.json()

        title = data.get("title", query)
        author = data.get("author", "Unknown")
        lyrics = data.get("lyrics", "")

        if not lyrics:
            await status.edit_text("❌ **Lyrics nahi mile!**")
            return

        # Telegram message limit 4096 chars
        header = f"📝 **{title}**\n🎤 Artist: **{author}**\n\n"
        if len(header + lyrics) > 4096:
            # Multiple messages mein bhejo
            lyrics_parts = [lyrics[i:i+3800] for i in range(0, len(lyrics), 3800)]
            await status.edit_text(header + lyrics_parts[0])
            for part in lyrics_parts[1:]:
                await message.reply_text(part)
        else:
            await status.edit_text(header + lyrics)

    except Exception as e:
        await status.edit_text(f"❌ **Error:** `{e}`")


@Client.on_message(filters.command("clean", prefixes=".") & filters.me)
async def clean_command(client: Client, message: Message):
    """🧹 .clean — Downloads folder saaf karo"""
    # Owner check
    if message.from_user and message.from_user.id != OWNER_ID:
        await message.edit_text("❌ **Sirf Owner ye command use kar sakta hai!**")
        return

    status = await message.edit_text("🧹 **Cleaning downloads...**")

    try:
        if os.path.exists(DOWNLOADS_DIR):
            count = len(os.listdir(DOWNLOADS_DIR))
            total_size = sum(
                os.path.getsize(os.path.join(DOWNLOADS_DIR, f))
                for f in os.listdir(DOWNLOADS_DIR)
                if os.path.isfile(os.path.join(DOWNLOADS_DIR, f))
            )
            size_mb = round(total_size / (1024 * 1024), 2)

            # Saari files delete karo
            shutil.rmtree(DOWNLOADS_DIR)
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)

            await status.edit_text(
                f"🧹 **Cleaned!**\n\n"
                f"🗑 Files deleted: `{count}`\n"
                f"💾 Space freed: `{size_mb} MB`"
            )
        else:
            await status.edit_text("📂 **Downloads folder already empty!**")
    except Exception as e:
        await status.edit_text(f"❌ **Error:** `{e}`")


@Client.on_message(filters.command("help", prefixes=".") & filters.me)
async def help_command(client: Client, message: Message):
    """❓ .help — Saare commands dikhao"""
    help_text = f"""[​]({DEFAULT_THUMB_URL})
🐍 **Cobra — Commands**

**🎶 Music (Voice Chat)**
├ `.play <link/query>` — Audio play in VC
├ `.vplay <link/query>` — Video play in VC
├ `.skip` — Skip current song
├ `.stop` — Stop + leave VC
├ `.pause` — Pause stream
├ `.resume` — Resume stream
├ `.queue` — Queue list
└ `.np` — Now playing info

**📥 Download**
├ `.song <query>` — Audio download + send
└ `.vsong <query>` — Video download + send

**🔧 Tools**
├ `.lyrics <song>` — Song lyrics
├ `.ping` — Bot alive check
├ `.stats` — Bot statistics
├ `.clean` — Clear downloads (Owner)
├ `.broadcast <msg>` — Broadcast (Owner)
└ `.help` — Ye message

**Made with ❤️ by Cobra 🐍**
"""
    await message.edit_text(help_text)
