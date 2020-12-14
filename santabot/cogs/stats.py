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
from pony import orm
from ..db.models import Server, User


class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(
            self,
            ctx: discord.ext.commands.Context,
            subject: typing.Union[discord.Member, str]
    ):
        with orm.db_session:
            await self.__make_stats(ctx, subject)

    async def __make_stats(
            self,
            ctx: discord.ext.commands.Context,
            subject: typing.Union[discord.Member, str]
    ):
        server = Server.get(id=ctx.guild.id)
        if (not server) or (not server.is_configured()):
            await ctx.send(
                '(error) No Webhook found for this server.\n'
                'Please ask an admin to use `@santa grinch summon`.'
            )
            return
        elif ctx.channel.id != server.channel_id:
            # Don't do anything if we're not in the same channel as
            # the Webhook
            return

        await ctx.trigger_typing()
        stats_user = None
        stats_user_db = None
        if isinstance(subject, discord.Member):
            stats_user = subject
            stats_user_db = self.bot.db.get_or_create(User, id=subject.id)
        elif subject == 'me':
            stats_user = ctx.author
            stats_user_db = self.bot.db.get_or_create(User, id=ctx.author.id)
        else:  # if argument is not "me" or a mention, give global stats (should it be like this)
            await ctx.send("global stats go here")
            return

        await ctx.send(
            f'stats for user {stats_user.mention}: '
            f'{stats_user_db.owned_present_count} owned presents'
        )


def setup(bot):
    bot.add_cog(Stats(bot))
