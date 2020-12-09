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


class Give(commands.Cog):
    """Parent class for commands that request presents.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def give(self, ctx,
                   recipient: typing.Union[discord.Member, str], *args):
        """Command to request a present for oneself or another User

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            recipient (typing.Union[discord.Member, str]): Either the recipient
                of the present (a Member), or the first word of the Present.
            *args: Words describing the Present.
        """
        await ctx.channel.trigger_typing()

        if isinstance(recipient, discord.Member):
            await ctx.send(
                'Ho ho ho {0}, check under your tree for {1} from {2}!'
                .format(recipient.mention,
                        " ".join(args),
                        ctx.author.mention))
        else:
            await ctx.send('Ho ho ho! Check under your tree for {0}!'
                           .format(" ".join(args)))

    @commands.command()
    async def please(self, ctx, _,
                     recipient: typing.Union[discord.Member, str],
                     *args):
        """Command for pleasantly asking for a present.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            _ ([type]): The `give` prefix. Not used.
            recipient (typing.Union[discord.Member, str]): Either the recipient
                of the present (a Member), or the first word of the Present.
            *args: Words describing the Present.
        """
        await ctx.channel.trigger_typing()

        await self.give(ctx, recipient, *args)
        await ctx.send('Thank you for saying please!')


def setup(bot):
    bot.add_cog(Give(bot))
