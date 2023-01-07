from aiocache import cached

from bot import Bot


class Config:
    @classmethod
    @cached(key="config_cache")
    async def fetch(cls, bot: "Bot"):
        return cls(await bot.db.config.find_one({"_id": 0}, {"_id": 0}) or {}, bot)

    def __init__(self, data: dict, bot: "Bot"):
        self.bot = bot
        self.role = data.get("role")
        self.staff_role = data.get("staff_role")
        self.staff_channel = data.get("staff_channel")

    def to_dict(self):
        return {
            "role": self.role,
            "staff_role": self.staff_role,
            "staff_channel": self.staff_channel,
        }

    async def save(self):
        await self.bot.db.config.replace_one({"_id": 0}, self.to_dict(), upsert=True)
