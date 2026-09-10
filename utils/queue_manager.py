from collections import defaultdict, deque
from typing import Optional


class QueueManager:
    """Per-chat song queue manager."""

    def __init__(self, max_size: int = 20):
        # Per-chat queues aur now playing tracking
        self.queues = defaultdict(deque)  # chat_id -> deque of song dicts
        self.now_playing = {}  # chat_id -> current song dict
        self.max_size = max_size

    def add(self, chat_id: int, song: dict) -> bool:
        """Queue mein song add karo. Returns False if queue full."""
        if len(self.queues[chat_id]) >= self.max_size:
            return False
        self.queues[chat_id].append(song)
        return True

    def next(self, chat_id: int) -> Optional[dict]:
        """Queue se next song nikalo."""
        if self.queues[chat_id]:
            song = self.queues[chat_id].popleft()
            self.now_playing[chat_id] = song
            return song
        return None

    def clear(self, chat_id: int):
        """Chat ki puri queue clear karo."""
        self.queues[chat_id].clear()
        self.now_playing.pop(chat_id, None)

    def get_queue(self, chat_id: int) -> list:
        """Chat ki queue list return karo."""
        return list(self.queues[chat_id])

    def get_now_playing(self, chat_id: int) -> Optional[dict]:
        """Abhi kya baj raha hai."""
        return self.now_playing.get(chat_id)

    def set_now_playing(self, chat_id: int, song: dict):
        """Current playing song set karo."""
        self.now_playing[chat_id] = song

    def is_empty(self, chat_id: int) -> bool:
        """Check karo queue khali hai ya nahi."""
        return len(self.queues[chat_id]) == 0

    def remove_now_playing(self, chat_id: int):
        """Now playing track ko remove karo."""
        self.now_playing.pop(chat_id, None)


queue = QueueManager()
