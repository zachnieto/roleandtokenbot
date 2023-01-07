import os
from typing import Any

import motor.motor_asyncio as motor
from disnake.ext import commands
from dotenv import load_dotenv


class Bot(commands.InteractionBot):
    def __init__(self, **options: Any):
        super().__init__(**options)
        load_dotenv()
        db_client = motor.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        self.db = db_client.bot
