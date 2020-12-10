#  Santa - A Discord Bot for engagement over the holidays.
#  Copyright (C) 2020  Ralph Drake
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.


import discord
import typing
from discord.ext import commands
from os import getenv
from ..grinch_manager import GrinchManager


class GrinchCommands(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        """Parent class for commands that manage the Grinch webhook.

        Args:
            bot (discord.ext.commands.Bot): The Bot loading the Cog.
        """
        self.bot = bot
        self.grinch = None
        self.webhook_name = getenv('WEBHOOK_NAME')
        self.webhook_avi_url = getenv('WEBHOOK_AVATAR_URL')

    @commands.group()
    @commands.has_permissions(manage_messages=True)
    async def grinch(self, ctx: discord.ext.commands.Context):
        """@santa grinch - Base command for Grinch webhook management commands.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        if ctx.invoked_subcommand is None:
            await ctx.channel.trigger_typing()

            if self.grinch:
                self.grinch.send_message('Yes? What do you want?')

            await ctx.send('Usage: `grinch <summon/banish>`')

    @grinch.command()
    @commands.has_permissions(manage_messages=True)
    async def summon(self,
                     ctx: discord.ext.commands.Context,
                     *,
                     from_cfg: typing.Optional[str]):
        """@santa grinch summon - Creates a webhook to send Grinch messages

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            from_cfg (str, optional): Uses webhook URL from config. For testing
        """
        await ctx.channel.trigger_typing()

        # Convert string command to boolean
        if isinstance(from_cfg, str):
            from_cfg = from_cfg.lower()
        from_cfg = from_cfg in ['from_cfg']
        webhook = None

        if from_cfg:
            # If we used @santa grinch summon from_cfg, we load the webhook URL
            # from our .env config. This will be superceded when database
            # storage and retrieval is developed.
            webhook = getenv('WEBHOOK_URL')
        else:
            # Creates a Webhook for the text channel _and_ a Webhook object
            # which we use for messaging.
            try:
                webhook = await ctx.channel.create_webhook(
                    name=self.webhook_name,
                    reason='{0} summoned {1}'.format(
                        ctx.author.display_name,
                        self.webhook_name
                    )
                )
            except discord.Forbidden:
                await ctx.send("I can't create a webhook for this channel.")
                return

            # The Webhook returned from create_webhook uses an async adapter,
            # but we want it to be synchronous. To fix this, we construct a new
            # Webhook object using our old one's ID and token.
            webhook = discord.Webhook.partial(
                webhook.id,
                webhook.token,
                adapter=discord.RequestsWebhookAdapter()
            )

        self.grinch = GrinchManager(
            webhook,
            self.webhook_name,
            self.webhook_avi_url
        )

        print('> {0}#{1} ({2}) created Webhook for channel #{3} ({4})'
              .format(ctx.author.name, ctx.author.discriminator,
                      ctx.author.mention, ctx.channel.name, ctx.channel.id))

        await ctx.send('{0} summoned the Grinch!'.format(ctx.author.mention))

        self.grinch.send_message(
            'Whats up lol im the Grinch.\n'
            'im here to steal your presents'
        )

    @grinch.command()
    @commands.has_permissions(manage_messages=True)
    async def banish(self, ctx: discord.ext.commands.Context):
        """@santa grinch banish - deletes the Grinch webhook

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        try:
            self.grinch.die(ctx.author.display_name)
            print('> {0}#{1} ({2}) banished the Grinch.'.format(
                ctx.author.name,
                ctx.author.discriminator,
                ctx.author.mention
            ))
        except discord.Forbidden:
            await ctx.send("Please give me the `manage webhook` permission.")
        else:
            await ctx.send('{0} banished the Grinch!'
                           .format(ctx.author.mention))
            self.grinch = None

    @grinch.command()
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: discord.ext.commands.Context, *, msg: str):
        """Make the Grinch say something. Used for debugging.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            msg (str): The message the Grinch will say.
        """
        if (self.grinch):
            self.grinch.send_message(msg)


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(GrinchCommands(bot))
