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


class Invite(commands.Cog):
    """Parent class for the invite command.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """@santa invite: Returns developer info to the requester.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        await ctx.channel.trigger_typing()
        await ctx.send(embed=discord.Embed(
            title='SantaBot',
            description='Created by the Podcast About List Code Monkeys'
        ).set_thumbnail(
            url=ctx.me.avatar_url
        ).add_field(
            name='Podcast About List',
            value=f'https://podaboutli.st/',
            inline=False
        ).add_field(
            name='Discord',
            value=f'https://podaboutli.st/discord',
            inline=False
        ).add_field(
            name='GitHub',
            value=f'https://github.com/Podcast-About-List/santa',
            inline=False
        ))


def setup(bot):
    bot.add_cog(Invite(bot))
