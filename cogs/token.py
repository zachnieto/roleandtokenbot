from disnake import (
    ApplicationCommandInteraction,
    Interaction,
    MessageInteraction,
    ModalInteraction,
)
from disnake.ext import commands
from disnake.ext.commands import MissingRole
from disnake.ui import Modal, TextInput, Button

from bot import Bot
from database.config import Config
from database.users import User
from predicates import has_required_role, required_role_pred


def setup(bot: "Bot"):
    bot.add_cog(Token(bot))


class Token(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    async def link_token(self, inter: "Interaction", api_token: str, secret_token: str):
        user = await User.fetch(inter.author.id, self.bot)
        user.api_token = api_token
        user.secret_token = secret_token

        config = await Config.fetch(self.bot)
        role = inter.guild.get_role(config.role)

        user.name = str(inter.author)
        user.enabled = role in inter.author.roles
        await user.save()

        await inter.send(
            f"Your API token has been linked to your account", ephemeral=True
        )

    @commands.slash_command()
    @has_required_role()
    async def token(
        self, inter: "ApplicationCommandInteraction", api_token: str, secret_token: str
    ):
        """Links your API token with your account

        Parameters
        ----------
        api_token: Your API token
        secret_token: Your secret token
        """
        await self.link_token(inter, api_token, secret_token)

    @commands.Cog.listener()
    async def on_button_click(self, inter: MessageInteraction):
        if inter.component.custom_id == "token_button":

            try:
                await required_role_pred(inter)
            except MissingRole as e:
                return await inter.send(str(e), ephemeral=True)

            token_input = TextInput(
                label=f"API Token",
                placeholder=f"token",
                custom_id="token_input",
                min_length=1,
                max_length=100,  # Probably some more precise requirements
                required=True,
            )
            secret_token_input = TextInput(
                label=f"API Secret",
                placeholder=f"secret",
                custom_id="secret_token_input",
                min_length=1,
                max_length=100,  # Probably some more precise requirements
                required=True,
            )
            await inter.response.send_modal(
                modal=Modal(
                    title="Link API Token",
                    custom_id="token_modal",
                    components=[token_input, secret_token_input],
                )
            )

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: ModalInteraction):
        api_token = inter.text_values["token_input"]
        secret_token = inter.text_values["secret_token_input"]
        await self.link_token(inter, api_token, secret_token)

    @commands.slash_command()
    @has_required_role()
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
