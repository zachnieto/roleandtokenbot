from disnake.ext.commands import check, MissingRole

from database.config import Config


async def required_role_pred(inter):
    config = await Config.fetch(inter.bot)
    role = inter.guild.get_role(config.role)

    if (
        inter.channel.permissions_for(inter.author).manage_channels
        or role in inter.author.roles
    ):
        return True

    raise MissingRole(role.name if role else "")


def has_required_role():
    return check(required_role_pred)
