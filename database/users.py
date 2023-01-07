from typing import List

from aiocache import cached

from bot import Bot


class User:
    @classmethod
    @cached(
        key_builder=lambda f, *args: f"user_cache_{args[1]}",
    )
    async def fetch(cls, user_id: int, bot: "Bot"):
        data = {"_id": user_id}
        return cls(await bot.db.user.find_one(data) or data, bot)

    def __init__(self, data: dict, bot: "Bot"):
        self.bot = bot
        self.id = data.get("_id")
        self.name = data.get("name")
        self.api_token = data.get("api_token")
        self.secret_token = data.get("secret_token")
        self.enabled = data.get("enabled", False)

    def to_dict(self):
        return {
            "name": self.name,
            "api_token": self.api_token,
            "secret_token": self.secret_token,
            "enabled": self.enabled,
        }

    async def save(self):
        await self.bot.db.user.replace_one(
            {"_id": self.id}, self.to_dict(), upsert=True
        )

    @staticmethod
    async def find_all(bot: "Bot") -> List["User"]:
        all_users = await bot.db.user.find().to_list(length=None)
        return [User(user, bot) for user in all_users]
