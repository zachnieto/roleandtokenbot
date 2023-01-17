from typing import TYPE_CHECKING

from disnake import ApplicationCommandInteraction, Permissions, Role, TextChannel
from disnake.ext import commands
from disnake.ui import Button

from database.config import Config
from database.users import User

if TYPE_CHECKING:
    from bot import Bot


def setup(bot: "Bot"):
    bot.add_cog(Staff(bot))


class Staff(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    @commands.slash_command(default_member_permissions=Permissions(administrator=True))
    async def linkbutton(self, inter: ApplicationCommandInteraction):
        """Sends a button which opens a API token linking Modal upon click"""
        await inter.channel.send(
            components=[
                Button(
                    label="Link Token",
                    custom_id="token_button",
                )
            ]
        )
        await inter.send(f"Button has been sent!", ephemeral=True)

    @commands.slash_command(default_member_permissions=Permissions(administrator=True))
    async def config(self, inter: ApplicationCommandInteraction):
        pass

    @config.sub_command()
    async def role(self, inter: ApplicationCommandInteraction, role: Role):
        """Set the required role for API access

        Parameters
        ----------
        role: Required role
        """

        config = await Config.fetch(self.bot)
        config.role = role.id
        await config.save()

        for user in await User.find_all(self.bot):
            member = await inter.guild.getch_member(user.id)
            user.enabled = member and role in member.roles
            await user.save()

        await inter.send(
            f"Required role has been set to {role.mention}", ephemeral=True
        )

    @config.sub_command_group()
    async def staff(self, inter: ApplicationCommandInteraction):
        pass

    @staff.sub_command(name="role")
    async def staffrole(self, inter: ApplicationCommandInteraction, role: Role):
        """Set the staff role to ping

        Parameters
        ----------
        role: Staff role
        """

        config = await Config.fetch(self.bot)
        config.staff_role = role.id
        await config.save()

        await inter.send(f"Staff role has been set to {role.mention}", ephemeral=True)

    @staff.sub_command()
    async def channel(self, inter: ApplicationCommandInteraction, channel: TextChannel):
        """Set the staff channel to send alerts

        Parameters
        ----------
        channel: The staff channel
        """

        config = await Config.fetch(self.bot)
        config.staff_channel = channel.id
        await config.save()

        await inter.send(
            f"Staff channel has been set to {channel.mention}", ephemeral=True
        )
