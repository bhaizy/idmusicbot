import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.youtube import YouTube
from utils.stream import stream_manager
from utils.queue_manager import queue
from utils.db import db
from config import DOWNLOADS_DIR, DEFAULT_THUMB_URL


@Client.on_message(filters.command("play", prefixes=".") & filters.me)
async def play_command(client: Client, message: Message):
    """🎵 .play <link/query> — Voice chat mein audio play karo"""
    await _handle_play(client, message, video=False)


@Client.on_message(filters.command("vplay", prefixes=".") & filters.me)
async def vplay_command(client: Client, message: Message):
    """🎬 .vplay <link/query> — Voice chat mein video play karo"""
    await _handle_play(client, message, video=True)


async def _handle_play(client: Client, message: Message, video: bool = False):
    """Play/VPlay ka common logic."""
    chat_id = message.chat.id
    
    # Save group/user to DB
    db.save_group(chat_id)
    if message.from_user:
        db.save_user(message.from_user.id)

    # Agar reply mein audio/voice file hai to direct download karke play karo
    replied = message.reply_to_message
    if replied and (replied.audio or replied.voice):
        status_msg = await message.edit_text("📥 **Downloading audio file...**")
        try:
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            dl_path = await replied.download(file_name=os.path.join(DOWNLOADS_DIR, ""))
            if not dl_path:
                await status_msg.edit_text("❌ **File download fail!**")
                return
            
            file_name = replied.audio.title if replied.audio and replied.audio.title else "Audio File"
            duration_str = "Unknown"
            if replied.audio and replied.audio.duration:
                mins = replied.audio.duration // 60
                secs = replied.audio.duration % 60
                duration_str = f"{mins}:{secs:02d}"
            
            song_info = {
                "title": file_name,
                "vidid": "local",
                "duration": duration_str,
                "thumbnail": DEFAULT_THUMB_URL,
                "file_path": dl_path,
                "is_video": False,
                "requester": message.from_user.first_name if message.from_user else "Unknown",
            }

            if stream_manager.is_active(chat_id):
                added = queue.add(chat_id, song_info)
                if added:
                    pos = len(queue.get_queue(chat_id))
                    await status_msg.edit_text(
                        f"[​]({DEFAULT_THUMB_URL})"
                        f"📋 **Added to Queue #{pos}**\n\n"
                        f"🎵 **{file_name}**\n"
                        f"👤 By: {song_info['requester']}"
                    )
                else:
                    await status_msg.edit_text("❌ **Queue full hai!**")
                return

            queue.set_now_playing(chat_id, song_info)
            success = await stream_manager.play(chat_id, dl_path, video=False)
            if success:
                await status_msg.edit_text(
                    f"[​]({DEFAULT_THUMB_URL})"
                    f"🎵 **Now Playing**\n\n"
                    f"🎵 **{file_name}**\n"
                    f"⏱ Duration: `{duration_str}`\n"
                    f"👤 By: {song_info['requester']}"
                )
            else:
                await status_msg.edit_text("❌ **Stream start nahi ho paya!**")
            return
        except Exception as e:
            await status_msg.edit_text(f"❌ **Error:** `{e}`")
            return

    # Query extract karo
    query = " ".join(message.command[1:]) if len(message.command) > 1 else None
    
    # Agar reply mein URL hai to woh use karo
    if not query and message.reply_to_message:
        url = await YouTube.get_url_from_message(message)
        if url:
            query = url
    
    if not query:
        await message.edit_text("❌ **Kuch to do bhai!**\n\nUsage: `.play <song name or YouTube link>`\nYa kisi audio file pe reply karo!")
        return

    status_msg = await message.edit_text(f"🔍 **Searching...** `{query}`")

    # Check if it's a YouTube link or search query
    is_yt_link = await YouTube.is_youtube_link(query)
    
    if is_yt_link:
        video_id = YouTube.extract_video_id(query)
        if not video_id:
            await status_msg.edit_text("❌ **Invalid YouTube link!**")
            return
        details = await YouTube.details(video_id, videoid=True)
    else:
        details = await YouTube.search(query)
    
    if not details:
        await status_msg.edit_text("❌ **Kuch nahi mila!** Try another search.")
        return

    title = details["title"]
    vidid = details["vidid"]
    duration = details.get("duration", "Unknown")
    thumbnail = details.get("thumbnail", "")

    await status_msg.edit_text(f"📥 **Downloading...** `{title}`")

    # Download audio or video
    if video:
        file_path = await YouTube.download_video(vidid)
    else:
        file_path = await YouTube.download_audio(vidid)

    if not file_path:
        await status_msg.edit_text("❌ **Download fail ho gaya!** Try again later.")
        return

    thumb_to_show = thumbnail if thumbnail else DEFAULT_THUMB_URL

    song_info = {
        "title": title,
        "vidid": vidid,
        "duration": duration,
        "thumbnail": thumb_to_show,
        "file_path": file_path,
        "is_video": video,
        "requester": message.from_user.first_name if message.from_user else "Unknown",
    }

    # Agar already playing hai to queue mein add karo
    if stream_manager.is_active(chat_id):
        added = queue.add(chat_id, song_info)
        if added:
            pos = len(queue.get_queue(chat_id))
            await status_msg.edit_text(
                f"[​]({thumb_to_show})"
                f"📋 **Added to Queue #{pos}**\n\n"
                f"🎵 **{title}**\n"
                f"⏱ Duration: `{duration}`\n"
                f"👤 By: {song_info['requester']}"
            )
        else:
            await status_msg.edit_text("❌ **Queue full hai!** Pehle kuch skip karo.")
        return

    # Pehla gaana — direct play
    queue.set_now_playing(chat_id, song_info)
    success = await stream_manager.play(chat_id, file_path, video=video)

    if success:
        emoji = "🎬" if video else "🎵"
        await status_msg.edit_text(
            f"[​]({thumb_to_show})"
            f"{emoji} **Now Playing**\n\n"
            f"🎵 **{title}**\n"
            f"⏱ Duration: `{duration}`\n"
            f"👤 By: {song_info['requester']}"
        )
    else:
        await status_msg.edit_text(
            "❌ **Stream start nahi ho paya!**\n\n"
            "Make sure:\n"
            "• Voice chat open hai\n"
            "• Bot ko admin rights hain"
        )
