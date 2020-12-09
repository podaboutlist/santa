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


class GrinchManager():
    def __init__(self, webhook, avatar_url='https://i.imgur.com/orRBRzi.png'):
        """Wrapper class for webhook logic that powers the Grinch's messages.

        Args:
            webhook (discord.Webhook): The Webhook for sending messages.
            avatar_url (str, optional): The URL of the Webhook avatar.
                Defaults to 'https://i.imgur.com/orRBRzi.png'.
        """
        # TODO: make this webhook persistent
        self.webhook = webhook
        self.avatar_url = avatar_url

    async def send_message(self, message):
        """Sends a message as the Grinch using a webhook.

        Args:
            message (str): The message to send.
        """
        await self.webhook.send(
            content=message,
            avatar_url=avatar_url
        )

    async def die(self, killer):
        """Remove the Grinch webhook

        Args:
            killer (str): The user who killed the Grinch
        """
        await self.webhook.delete(
                reason='{0} banished the Grinch'.format(killer)
            )
        print('> {0} banished the Grinch.')


class GrinchCommands(commands.Cog):
    def __init__(self, bot):
        """Parent class for commands that manage the Grinch webhook.

        Args:
            bot (discord.ext.commands.Bot): The Bot loading the Cog.
        """
        self.bot = bot
        self.grinch = None

    @commands.group()
    @commands.has_permissions(manage_messages=True)
    async def grinch(self, ctx):
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
    async def summon(self, ctx):
        """@santa grinch summon - Creates a webhook to send Grinch messages

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        await ctx.channel.trigger_typing()

        try:
            webhook = await ctx.channel.create_webhook(
                name='The Grinch',
                reason='{0} summoned the Grinch'
                       .format(ctx.author.display_name)
            )
        except discord.Forbidden:
            await ctx.send("I can't create a webhook for this channel.")
            return

        print('Webhook created for channel {0}'.format(ctx.channel.name))

        self.grinch = GrinchManager(webhook)
        await ctx.send('{0} summoned the Grinch!'.format(ctx.author.mention))
        await self.grinch.send_message('Whats up lol im the Grinch.')
        await self.grinch.send_message('im here to steal your presents')

    @grinch.command()
    @commands.has_permissions(manage_messages=True)
    async def banish(self, ctx):
        """@santa grinch banish - deletes the Grinch webhook

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        try:
            await self.grinch.die(ctx.author.display_name)
        except discord.Forbidden:
            await ctx.send("Please give me the `manage webhook` permission.")
        else:
            await ctx.send('{0} banished the Grinch!'
                           .format(ctx.author.mention))


def setup(bot):
    bot.add_cog(GrinchCommands(bot))
