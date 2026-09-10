import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from utils.db import db


@Client.on_message(filters.command("broadcast", prefixes=".") & filters.me)
async def broadcast_command(client: Client, message: Message):
    """📢 .broadcast — Sabko message bhejo (Owner only)"""
    # Owner check
    if message.from_user and message.from_user.id != OWNER_ID:
        await message.edit_text("❌ **Sirf Owner broadcast kar sakta hai!**")
        return

    # Broadcast message get karo
    broadcast_msg = None
    broadcast_text = None

    if message.reply_to_message:
        broadcast_msg = message.reply_to_message
    elif len(message.command) > 1:
        broadcast_text = " ".join(message.command[1:])
    else:
        await message.edit_text(
            "❌ **Kuch to do broadcast karne ke liye!**\n\n"
            "Usage:\n"
            "• `.broadcast <message>` — Text broadcast\n"
            "• `.broadcast` (reply to a message) — Forward broadcast"
        )
        return

    users = db.get_all_users()
    groups = db.get_all_groups()
    total = len(users) + len(groups)

    if total == 0:
        await message.edit_text("❌ **Database mein koi user/group nahi hai!**")
        return

    status = await message.edit_text(
        f"📢 **Broadcasting...**\n\n"
        f"👤 Users: {len(users)}\n"
        f"👥 Groups: {len(groups)}\n"
        f"📊 Total: {total}"
    )

    sent = 0
    failed = 0

    # Users ko send karo
    for user_id in users:
        try:
            if broadcast_msg:
                await broadcast_msg.forward(user_id)
            else:
                await client.send_message(user_id, broadcast_text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.3)  # Flood avoid karo

    # Groups ko send karo
    for chat_id in groups:
        try:
            if broadcast_msg:
                await broadcast_msg.forward(chat_id)
            else:
                await client.send_message(chat_id, broadcast_text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.3)

    await status.edit_text(
        f"📢 **Broadcast Complete!**\n\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total: {total}"
    )
