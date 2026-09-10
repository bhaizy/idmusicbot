from pyrogram import Client, filters
from pyrogram.types import Message
from utils.stream import stream_manager
from utils.queue_manager import queue


@Client.on_message(filters.command("skip", prefixes=".") & filters.me)
async def skip_command(client: Client, message: Message):
    """⏭️ .skip — Current song skip karo"""
    chat_id = message.chat.id

    if not stream_manager.is_active(chat_id):
        await message.edit_text("❌ **Kuch play nahi ho raha!**")
        return

    next_song = await stream_manager.skip(chat_id)
    if next_song:
        await message.edit_text(
            f"⏭️ **Skipped!** Now Playing:\n\n"
            f"🎵 **{next_song['title']}**\n"
            f"⏱ Duration: `{next_song.get('duration', 'Unknown')}`"
        )
    else:
        await message.edit_text("⏭️ **Skipped!** Queue empty — voice chat leave kar diya.")


@Client.on_message(filters.command("stop", prefixes=".") & filters.me)
async def stop_command(client: Client, message: Message):
    """⏹️ .stop — Music stop + VC leave"""
    chat_id = message.chat.id

    if not stream_manager.is_active(chat_id):
        await message.edit_text("❌ **Kuch play nahi ho raha!**")
        return

    await stream_manager.stop(chat_id)
    await message.edit_text("⏹️ **Music stopped!** Voice chat se nikal gaya.")


@Client.on_message(filters.command("pause", prefixes=".") & filters.me)
async def pause_command(client: Client, message: Message):
    """⏸️ .pause — Stream pause karo"""
    chat_id = message.chat.id

    if not stream_manager.is_active(chat_id):
        await message.edit_text("❌ **Kuch play nahi ho raha!**")
        return

    success = await stream_manager.pause(chat_id)
    if success:
        await message.edit_text("⏸️ **Paused!** Resume karne ke liye `.resume` type karo.")
    else:
        await message.edit_text("❌ **Pause nahi ho paya!**")


@Client.on_message(filters.command("resume", prefixes=".") & filters.me)
async def resume_command(client: Client, message: Message):
    """▶️ .resume — Paused stream resume karo"""
    chat_id = message.chat.id

    if not stream_manager.is_active(chat_id):
        await message.edit_text("❌ **Kuch play nahi ho raha!**")
        return

    success = await stream_manager.resume(chat_id)
    if success:
        await message.edit_text("▶️ **Resumed!** Music wapas shuru ho gaya.")
    else:
        await message.edit_text("❌ **Resume nahi ho paya!**")
