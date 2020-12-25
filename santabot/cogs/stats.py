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
        await self.__make_stats(ctx, subject)

    # -------------------------------------------------------------------------
    # __make_stats() handles the stats logic
    # -------------------------------------------------------------------------
    @orm.db_session
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
            all_time_presents = self.calculate_all_time_presents()
            active_presents = self.calculate_active_presents()
            stolen_presents = all_time_presents - active_presents
            self_presents = self.calculate_all_self_presents()
            non_self_presents = active_presents - self_presents
            please_count = self.calculate_please()
            non_please_count = all_time_presents - please_count
            await ctx.send(embed=discord.Embed(
                title='Stats for the server'
            ).set_thumbnail(
                url=ctx.guild.icon_url
            ).add_field(
                name='Total presents given',
                value=f'{all_time_presents} presents have been gifted, '
                      f'of which {stolen_presents} were stolen by The Grinch.',
                inline=False
            ).add_field(
                name='Successful presents',
                value=f'Of the {active_presents} presents that found their '
                      f'way to their recipients, {self_presents} were given '
                      f'by their owners to themselves and {non_self_presents} '
                      f'were given to someone else.',
                inline=False
            ).add_field(
                name="The magic word",
                value=f'{please_count} users have said please when asking '
                      f'for a present, while {non_please_count} were rude '
                      f'little children who did not',
                inline=False
            ).set_footer(
                text='To see your personal stats, '
                     'use "@santa stats me"\n'
                     'To see another user\'s stats, '
                     'use "@santa stats @username"',
                icon_url=ctx.me.avatar_url
            ))
            return

        await ctx.send(embed=discord.Embed(
            title=f'Stats for {stats_user.display_name}'
        ).set_thumbnail(
            url=stats_user.avatar_url
        ).add_field(
            name='Owned',
            value=f'{stats_user_db.owned_present_count}',
            inline=True
        ).add_field(
            name='Stolen',
            value=f'{stats_user_db.stolen_present_count}',
            inline=True
        ).add_field(
            name='Gifted',
            value=f'{stats_user_db.gifted_present_count}',
            inline=True
        ).add_field(
            name='Grinch Visits',
            value=f'{stats_user_db.grinch_visit_count}',
            inline=False
        ).set_footer(
            text='Try "@santa stats global" for global stats',
            icon_url=ctx.me.avatar_url
        ))

    # -------------------------------------------------------------------------
    # Discord.py `top` command
    # -------------------------------------------------------------------------
    @commands.command()
    async def top(
            self,
            ctx: discord.ext.commands.Context,
    ):
        """Command to get the top 10 for the server

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
        """
        embed = discord.Embed(
            title='Leaderboard',
            description='These users have the most presents'
        ).set_thumbnail(
            url=ctx.guild.icon_url
        )
        for i, user_obj in enumerate(self.users_by_present()):
            if i > 10:
                break
            user = self.bot.get_user(user_obj.id)
            embed.add_field(
                name=f'{i}: {user.mention}',
                value=f'{user.owned_present_count} presents'
            )
        embed.set_footer(
            text='Try "@santa about" to learn more about me',
            icon_url=ctx.me.avatar_url
        )
        pass

    @orm.db_session
    def users_by_present(self):
        return orm.select(
            u for u in User
        ).order_by(
            lambda u: u.owned_present_count
        ).page(1)

    @orm.db_session
    def calculate_all_time_presents(self) -> int:
        """Calculate all time number of presents distributed.

        Returns:
            int: All time number of presents distributed.
        """
        return orm.count(p for p in self.bot.db.Present)

    @orm.db_session
    def calculate_active_presents(self) -> int:
        """Calculate how many presents are currently not 'stolen'

        Returns:
            int: Number of non-stolen presents.
        """
        return orm.count(p for p in self.bot.db.Present if not p.stolen)

    @orm.db_session
    def calculate_all_stolen_presents(self) -> int:
        """Calculate how many presents are currently 'stolen'

        Returns:
            int: Number of stolen presents.
        """
        return orm.count(p for p in self.bot.db.Present if p.stolen)

    @orm.db_session
    def calculate_all_self_presents(self) -> int:
        """Calculate how many presents were given to a user by themselves

        Returns:
            int: Number of self-gifted presents.
        """
        return orm.count(
            p for p in self.bot.db.Present
            if not p.stolen and p.owner.id == p.gifter.id
        )

    @orm.db_session
    def calculate_please(self) -> int:
        """Calculate how many presents were given to a user by themselves

        Returns:
            int: Number of self-gifted presents.
        """
        return orm.count(p for p in self.bot.db.Present if p.please)


def setup(bot):
    bot.add_cog(Stats(bot))
