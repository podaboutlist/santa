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


class About(commands.Cog):
    """Parent class for the about command.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def about(self, ctx: commands.Context):
        """@santa about: Returns developer info to the requester.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        await ctx.channel.trigger_typing()
        await ctx.send(embed=discord.Embed(
            title='About SantaBot',
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
        ).add_field(
            name='Want SantaBot on your server?',
            value=f'[Click here to add SantaBot to your server]'
                  f'(https://discord.com/oauth2/authorize?client_id='
                  f'785952609592016896&scope=bot&permissions=537250880)',
            inline=False
        ).set_footer(
            text='Created by the Podcast About List Code Monkeys'
        ))


def setup(bot):
    bot.add_cog(About(bot))
