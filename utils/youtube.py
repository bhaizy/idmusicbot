import os
import re
import aiohttp
from typing import Union, Optional
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
from config import MEOW_API_URL, MEOW_API_KEY, DOWNLOADS_DIR


def time_to_seconds(time_str: str) -> int:
    """Duration string ko seconds mein convert karo (e.g., '3:45' -> 225)"""
    try:
        parts = str(time_str).split(":")
        return sum(int(x) * 60 ** i for i, x in enumerate(reversed(parts)))
    except Exception:
        return 0


async def download_song(video_id: str) -> Optional[str]:
    """Yuki API se audio download karo."""
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOADS_DIR, f"{video_id}.mp3")

    # Agar already downloaded hai to skip
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            stream_url = f"{MEOW_API_URL}/stream/{video_id}?key={MEOW_API_KEY}&type=audio&quality=128"
            async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status != 200:
                    return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None


async def download_video(video_id: str) -> Optional[str]:
    """Yuki API se video download karo."""
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOADS_DIR, f"{video_id}.mp4")

    # Agar already downloaded hai to skip
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            stream_url = f"{MEOW_API_URL}/stream/{video_id}?key={MEOW_API_KEY}&type=video&quality=480"
            async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status != 200:
                    return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None


class YouTubeAPI:
    """YouTube search aur details fetch karne ke liye class."""

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def search(self, query: str) -> Optional[dict]:
        """YouTube pe search karo, first result return karo."""
        try:
            results = VideosSearch(query, limit=1)
            data = (await results.next())["result"]
            if not data:
                return None
            result = data[0]
            return {
                "title": result["title"],
                "vidid": result["id"],
                "duration": result.get("duration", "0:00"),
                "thumbnail": result["thumbnails"][0]["url"].split("?")[0],
                "link": result["link"],
            }
        except Exception:
            return None

    async def details(self, link: str, videoid: bool = False) -> Optional[dict]:
        """Video ki details fetch karo."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            data = (await results.next())["result"]
            if not data:
                return None
            result = data[0]
            duration_min = result.get("duration", "0:00")
            return {
                "title": result["title"],
                "vidid": result["id"],
                "duration": duration_min,
                "duration_sec": time_to_seconds(duration_min),
                "thumbnail": result["thumbnails"][0]["url"].split("?")[0],
                "link": result["link"],
            }
        except Exception:
            return None

    async def is_youtube_link(self, link: str) -> bool:
        """Check karo ye YouTube link hai ya nahi."""
        return bool(re.search(self.regex, link))

    def extract_video_id(self, link: str) -> Optional[str]:
        """YouTube link se video ID nikalo."""
        patterns = [
            r"(?:v=|/)([0-9A-Za-z_-]{11}).*",
            r"(?:youtu\.be/)([0-9A-Za-z_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return match.group(1)
        return None

    async def get_url_from_message(self, message: Message) -> Optional[str]:
        """Message se URL extract karo."""
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        for msg in messages:
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        return text[entity.offset: entity.offset + entity.length]
            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def download_audio(self, video_id: str) -> Optional[str]:
        """Audio download karo via Yuki API."""
        return await download_song(video_id)

    async def download_video(self, video_id: str) -> Optional[str]:
        """Video download karo via Yuki API."""
        return await download_video(video_id)

    async def playlist(self, link: str, limit: int = 20) -> list:
        """Playlist se video IDs fetch karo."""
        if "&" in link:
            link = link.split("&")[0]
        try:
            plist = await Playlist.get(link)
            videos = plist.get("videos") or []
            return [v["id"] for v in videos[:limit] if v and v.get("id")]
        except Exception:
            return []


YouTube = YouTubeAPI()
