from pyrogram import Client, filters
from pyrogram.types import Message
from utils.queue_manager import queue
from utils.stream import stream_manager
from config import DEFAULT_THUMB_URL


@Client.on_message(filters.command("queue", prefixes=".") & filters.me)
async def queue_command(client: Client, message: Message):
    """📋 .queue — Queue list dikhao"""
    chat_id = message.chat.id
    songs = queue.get_queue(chat_id)
    now = queue.get_now_playing(chat_id)

    if not now and not songs:
        await message.edit_text("📋 **Queue khali hai!** `.play` se gaana add karo.")
        return

    text = f"[​]({DEFAULT_THUMB_URL})📋 **Music Queue**\n\n"

    if now:
        text += f"▶️ **Now Playing:** {now['title']} [`{now.get('duration', '?')}`]\n\n"

    if songs:
        text += "**Up Next:**\n"
        for i, song in enumerate(songs, 1):
            text += f"`{i}.` {song['title']} [`{song.get('duration', '?')}`]\n"
    else:
        text += "_Queue mein aur koi gaana nahi hai._"

    await message.edit_text(text)


@Client.on_message(filters.command("np", prefixes=".") & filters.me)
async def now_playing_command(client: Client, message: Message):
    """🎧 .np — Now Playing info"""
    chat_id = message.chat.id
    now = queue.get_now_playing(chat_id)

    if not now:
        if not stream_manager.is_active(chat_id):
            await message.edit_text("🎧 **Abhi kuch nahi baj raha!**")
            return
        await message.edit_text("🎧 **Playing...** but song info available nahi hai.")
        return

    thumb = now.get("thumbnail") or DEFAULT_THUMB_URL

    text = (
        f"[​]({thumb})"
        f"🎧 **Now Playing**\n\n"
        f"🎵 **{now['title']}**\n"
        f"⏱ Duration: `{now.get('duration', 'Unknown')}`\n"
        f"👤 Requested by: {now.get('requester', 'Unknown')}\n"
    )

    if now.get('is_video'):
        text += "📺 Mode: Video\n"
    else:
        text += "🔊 Mode: Audio\n"

    queue_list = queue.get_queue(chat_id)
    text += f"\n📋 Queue: {len(queue_list)} songs remaining"

    await message.edit_text(text)
