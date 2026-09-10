import os
from tinydb import TinyDB, Query
from datetime import datetime


class Database:
    """TinyDB based database for storing users, groups, aur stats."""

    def __init__(self):
        # Database directory aur TinyDB file initialize karo
        os.makedirs("data", exist_ok=True)
        self.db = TinyDB("data/db.json")
        self.users = self.db.table("users")
        self.groups = self.db.table("groups")
        self.stats = self.db.table("stats")
        # Initialize stats if empty
        if not self.stats.all():
            self.stats.insert({"songs_played": 0, "started_at": str(datetime.now())})

    def save_user(self, user_id: int):
        """User ko database mein save karo agar pehle se nahi hai."""
        User = Query()
        if not self.users.search(User.user_id == user_id):
            self.users.insert({"user_id": user_id})

    def save_group(self, chat_id: int):
        """Group ko database mein save karo agar pehle se nahi hai."""
        Group = Query()
        if not self.groups.search(Group.chat_id == chat_id):
            self.groups.insert({"chat_id": chat_id})

    def get_all_users(self) -> list:
        """Database se saare users ki user_id list return karo."""
        return [u["user_id"] for u in self.users.all()]

    def get_all_groups(self) -> list:
        """Database se saare groups ki chat_id list return karo."""
        return [g["chat_id"] for g in self.groups.all()]

    def increment_songs(self):
        """Total played songs count ko 1 se badhao."""
        all_stats = self.stats.all()
        if all_stats:
            current = all_stats[0].get("songs_played", 0)
            self.stats.update({"songs_played": current + 1})

    def get_stats(self) -> dict:
        """Bot ke overall stats return karo (users, groups, songs played)."""
        all_stats = self.stats.all()
        return {
            "users": len(self.users.all()),
            "groups": len(self.groups.all()),
            "songs_played": all_stats[0].get("songs_played", 0) if all_stats else 0,
            "started_at": all_stats[0].get("started_at", "Unknown") if all_stats else "Unknown",
        }


db = Database()
