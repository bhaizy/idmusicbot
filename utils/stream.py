import os
import asyncio
from typing import Optional
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioVideoPiped
from pytgcalls.types.stream import StreamAudioEnded
from utils.queue_manager import queue
from utils.youtube import YouTube
from utils.db import db


class StreamManager:
    """PyTgCalls stream manager voice chat streaming ke liye."""

    def __init__(self):
        self.pytgcalls: Optional[PyTgCalls] = None
        self.active_chats = set()  # Currently streaming chats

    def setup(self, pytgcalls_instance: PyTgCalls):
        """PyTgCalls instance set karo aur stream end callback register karo."""
        self.pytgcalls = pytgcalls_instance

        @self.pytgcalls.on_stream_end()
        async def on_stream_end(client, update: StreamAudioEnded):
            """Jab gaana khatam ho jaye, next gaana play karo."""
            chat_id = update.chat_id
            await self._play_next(chat_id)

    async def play(self, chat_id: int, file_path: str, video: bool = False):
        """Voice chat mein audio/video stream karo."""
        try:
            if video:
                stream = AudioVideoPiped(file_path)
            else:
                stream = AudioPiped(file_path)

            if chat_id in self.active_chats:
                await self.pytgcalls.change_stream(chat_id, stream)
            else:
                await self.pytgcalls.join_group_call(chat_id, stream)
                self.active_chats.add(chat_id)

            db.increment_songs()
            return True
        except Exception as e:
            print(f"Stream Error: {e}")
            return False

    async def _play_next(self, chat_id: int):
        """Queue se next song play karo."""
        next_song = queue.next(chat_id)
        if next_song:
            file_path = next_song.get("file_path")
            is_video = next_song.get("is_video", False)
            if file_path and os.path.exists(file_path):
                await self.play(chat_id, file_path, video=is_video)
                return next_song
        # Queue empty ho gayi — voice chat leave karo
        await self.stop(chat_id)
        return None

    async def skip(self, chat_id: int) -> Optional[dict]:
        """Current track skip karo aur next track play karo."""
        return await self._play_next(chat_id)

    async def stop(self, chat_id: int):
        """Music stop karo aur voice chat leave karo."""
        try:
            queue.clear(chat_id)
            if chat_id in self.active_chats:
                await self.pytgcalls.leave_group_call(chat_id)
                self.active_chats.discard(chat_id)
            # Clean up downloaded files
            self._cleanup_files(chat_id)
        except Exception as e:
            print(f"Stop Error: {e}")
            self.active_chats.discard(chat_id)

    async def pause(self, chat_id: int) -> bool:
        """Stream ko pause karo."""
        try:
            await self.pytgcalls.pause_stream(chat_id)
            return True
        except Exception:
            return False

    async def resume(self, chat_id: int) -> bool:
        """Stream ko resume karo."""
        try:
            await self.pytgcalls.resume_stream(chat_id)
            return True
        except Exception:
            return False

    def is_active(self, chat_id: int) -> bool:
        """Check karo voice chat active hai ya nahi."""
        return chat_id in self.active_chats

    def _cleanup_files(self, chat_id: int):
        """Downloaded files cleanup (optional)."""
        pass  # Periodic cleanup implement kar sakte hain


stream_manager = StreamManager()
