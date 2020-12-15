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
from ..db.models import Present, Server, User


class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -------------------------------------------------------------------------
    # Discord.py `stats` command
    # -------------------------------------------------------------------------
    @commands.command()
    async def stats(
            self,
            ctx: discord.ext.commands.Context,
            subject: typing.Union[discord.Member, str]
    ):
        """Command to get stats for a player or the server

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            subject (discord.Member or str): Either a User @mention or a
                word like 'me'.
        """
        with orm.db_session:
            await self.__make_stats(ctx, subject)

    # -------------------------------------------------------------------------
    # __make_stats() handles the stats logic
    # -------------------------------------------------------------------------
    async def __make_stats(
            self,
            ctx: discord.ext.commands.Context,
            subject: typing.Union[discord.Member, str]
    ):
        """Underlying logic for `@santa stats`

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            subject (discord.Member or str): Either a User @mention or a
                word like 'me'.
        """
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
        else:  # if argument is not "me" or a mention, give global stats
            all_time_presents = Present.calculate_all_time_presents()
            active_presents = Present.calculate_active_presents()
            stolen_presents = all_time_presents - active_presents
            self_presents = Present.calculate_all_self_presents()
            non_self_presents = active_presents - self_presents
            please_count = Present.calculate_please()
            non_please_count = all_time_presents - please_count
            await ctx.send(
                f"Stats for the server:\n"
                f"{all_time_presents} have been gifted, "
                f"{stolen_presents} of which were stolen by The Grinch.\n"
                f"Of the {active_presents} that found their way to their "
                f"recipients, {self_presents} were given by their owners "
                f"to themselves and {non_self_presents} were given to "
                f"someone else.\n{please_count} users have said please "
                f"when asking for a gift, while {non_please_count} "
                f"rude children did not.\n"
                f"To see your personal stats, use `@santa stats me`.\n"
                f"To see another user's stats, use `@santa stats @username`."
            )
            return

        await ctx.send(
            f'Stats for {stats_user.mention}:\n'
            f'- {stats_user_db.owned_present_count} owned presents\n'
            f'- {stats_user_db.stolen_present_count} stolen presents\n'
            f'- {stats_user_db.gifted_present_count} gifted presents\n'
            f'- {stats_user_db.grinch_visit_count} visits from the grinch'
        )


def setup(bot):
    bot.add_cog(Stats(bot))
