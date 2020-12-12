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
from pony import orm
from ..db.models import Server
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
    async def summon(
        self,
        ctx: discord.ext.commands.Context,
        *,
        from_cfg: typing.Optional[str]
    ):
        """@santa grinch summon - Creates a webhook to send Grinch messages

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            from_cfg (str, optional): Uses webhook URL from config. For testing
        """
        # Check if this server is already registered in the DB
        with orm.db_session:
            server = self.bot.db.get_or_create(Server, id=ctx.guild.id)
            new_webhook = None

            if server.is_configured():
                self.grinch = GrinchManager(server.webhook_url)
                self.grinch.send_message('You already summoned me here >:)')
                return

            await ctx.channel.trigger_typing()

            # Create a new Webhook since this Server doesn't have one
            try:
                new_webhook = await ctx.channel.create_webhook(
                    name=self.webhook_name,
                    reason='{0} summoned {1}'.format(
                        ctx.author.display_name,
                        self.webhook_name
                    )
                )
            except discord.Forbidden:
                await ctx.send(
                    "(error) I can't create a webhook for this channel."
                )
                return

            server.add_webhook(
                channel_id=ctx.channel.id,
                webhook_url=new_webhook.url
            )

            self.grinch = GrinchManager(new_webhook.url)

            # End of orm.db_session context

        print('> {0}#{1} ({2}) created Webhook for channel #{3} ({4})'.format(
            ctx.author.name,
            ctx.author.discriminator,
            ctx.author.mention,
            ctx.channel.name,
            ctx.channel.id
        ))

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
        reason = '{0} banished the Grinch!'

        # Delete the Webhook URL from the DB
        with orm.db_session:
            server = Server.get(id=ctx.guild.id)

            if (not server) or (not server.is_configured()):
                await ctx.send(
                    "(error) This server doesn't have an associated Webhook."
                )
                return

            # Remove Wenook information from the DB
            server.remove_webhook()

            # End of orm.db_session context

        # Remove the Webhook from the Discord Guild
        try:
            self.grinch.webhook.delete(
                reason=reason.format((
                    ctx.author.name,
                    "#",
                    ctx.author.discriminator
                ))
            )
        except AttributeError:
            # self.grinch or self.grinch.webhook doesn't exist
            pass
        except discord.Forbidden:
            await ctx.send("Please give me the `manage webhooks` permission.")
            return
        except discord.NotFound:
            await ctx.send('(error): Webhook not found. Already deleted?')

        print('> {0}#{1} ({2}) deleted Webhook for channel #{3} ({4})'.format(
            ctx.author.name,
            ctx.author.discriminator,
            ctx.author.mention,
            ctx.channel.name,
            ctx.channel.id
        ))

        await ctx.send(reason.format(ctx.author.mention))
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
        else:
            await ctx.send('No one has added the Grinch to this channel yet.')


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(GrinchCommands(bot))
