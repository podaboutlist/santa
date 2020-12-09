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
    async def summon(self, ctx: discord.ext.commands.Context):
        """@santa grinch summon - Creates a webhook to send Grinch messages

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        await ctx.channel.trigger_typing()

        try:
            webhook = await ctx.channel.create_webhook(
                name=self.webhook_name,
                reason='{0} summoned {1}'
                       .format(ctx.author.display_name, self.webhook_name)
            )
        except discord.Forbidden:
            await ctx.send("I can't create a webhook for this channel.")
            return

        print('> {0}#{1} ({2}) created Webhook for channel #{3} ({4})'
              .format(ctx.author.name, ctx.author.discriminator,
                      ctx.author.mention, ctx.channel.name, ctx.channel.id))

        self.grinch = GrinchManager(
            webhook,
            self.webhook_name,
            self.webhook_avi_url
        )
        await ctx.send('{0} summoned the Grinch!'.format(ctx.author.mention))
        await self.grinch.send_message('Whats up lol im the Grinch.')
        await self.grinch.send_message('im here to steal your presents')

    @grinch.command()
    @commands.has_permissions(manage_messages=True)
    async def banish(self, ctx: discord.ext.commands.Context):
        """@santa grinch banish - deletes the Grinch webhook

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        try:
            await self.grinch.die(ctx.author.display_name)
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


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(GrinchCommands(bot))
