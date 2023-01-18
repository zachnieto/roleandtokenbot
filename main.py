import os

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import CheckFailure
from dotenv import load_dotenv

from bot import Bot
from database.config import Config
from database.users import User

intents = disnake.Intents.default()
intents.members = True

bot = Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


@bot.listen()
async def on_member_update(before: disnake.Member, after: disnake.Member):
    config = await Config.fetch(bot)
    role = before.guild.get_role(config.role)
    if role is None:
        return

    user = await User.fetch(before.id, bot)
    # Lost the role
    if role in before.roles and role not in after.roles:
        user.enabled = False
        await user.save()
        embed = disnake.Embed(
            title="Role Lost",
            description=f"{before.mention} lost the {role.mention} role",
            color=disnake.Color.red(),
        )
        channel = before.guild.get_channel(config.staff_channel)
        if channel is not None:
            staff_role = before.guild.get_role(config.staff_role)
            await channel.send(
                content=staff_role.mention if staff_role else None, embed=embed
            )
    # Gained the role
    elif role not in before.roles and role in after.roles:
        user.enabled = True
        await user.save()
        embed = disnake.Embed(
            title="Role Gained",
            description=f"{before.mention} gained the {role.mention} role",
            color=disnake.Color.green(),
        )
        channel = before.guild.get_channel(config.staff_channel)
        if channel is not None:
            staff_role = before.guild.get_role(config.staff_role)
            await channel.send(
                content=staff_role.mention if staff_role else None, embed=embed
            )

@bot.listen()
async def on_slash_command_error(inter: ApplicationCommandInteraction, error):
    error = getattr(error, "original", error)

    if isinstance(error, CheckFailure):
        return await inter.send(str(error), ephemeral=True)

    raise error


if __name__ == "__main__":
    load_dotenv()
    bot.load_extensions("./cogs")
    bot.run(os.getenv("BOT_TOKEN"))
