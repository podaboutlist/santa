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
from random import randint
from math import ceil
from ..db.models import Present, Server, User
from ..grinch_manager import GrinchManager


class Give(commands.Cog):
    """Parent class for commands that request presents.
    """

    def __init__(self, bot):
        self.bot = bot
        self.please = False

    # -------------------------------------------------------------------------
    # Discord.py `give` command
    # -------------------------------------------------------------------------
    @commands.command()
    async def give(
        self,
        ctx: discord.ext.commands.Context,
        recipient: typing.Union[discord.Member, str],
        *,
        present_name: str
    ):
        """Command to request a present for oneself or another User

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            recipient (discord.Member or str): Either a User @mention or a
                word like 'me'.
            present_name (str): The name of the present.
        """
        if isinstance(recipient, str) and recipient.lower() != "me":
            # They said something other than a username or "me"
            return

        with orm.db_session:
            try:
                await self.__do_gifting(ctx, recipient, present_name)
            except e:
                await ctx.send(
                    'There was an error processing your command:\n'
                    '```python\n'
                    '{0}\n'format(e)
                    '```'
                )
                raise e

    # -------------------------------------------------------------------------
    # Discord.py `please` prefix for `give` command
    # -------------------------------------------------------------------------
    @commands.command()
    async def please(
        self,
        ctx: discord.ext.commands.Context,
        give: str,  # give
        recipient: typing.Union[discord.Member, str],  # @user or 'me'
        *,
        present_name: str
    ):
        """Command for pleasantly asking for a present.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            give (str): The `give` prefix. If not "give," command doesn't do
                anything.
            recipient (discord.Member or str]): Either the recipient of the
                present (a Member), or the first word of the Present.
            present_name (str): The name of the present.
        """
        if give.lower() != 'give':
            # They said something other than "please give"
            return

        with orm.db_session:
            try:
                await self.__do_gifting(
                    ctx,
                    recipient,
                    present_name,
                    please=True
                )
            except e:
                await ctx.send(
                    'There was an error processing your command:\n'
                    '```python\n'
                    '{0}\n'format(e)
                    '```'
                )
                raise e

    # -------------------------------------------------------------------------
    # Discord.py `gimme` command, equivalent to `give me`
    # -------------------------------------------------------------------------
    @commands.command()
    async def gimme(
        self,
        ctx: discord.ext.commands.Context,
        *,
        present_name: str
    ):
        """Command to request a present for oneself

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            present_name (str): The name of the present.
        """
        with orm.db_session:
            try:
                await self.__do_gifting(ctx, 'me', present_name)
            except e:
                await ctx.send(
                    'There was an error processing your command:\n'
                    '```python\n'
                    '{0}\n'format(e)
                    '```'
                )
                raise e

    # -------------------------------------------------------------------------
    # __do_gifting() handles the majority of the gift sending logic
    # -------------------------------------------------------------------------
    async def __do_gifting(
        self,
        ctx: discord.ext.commands.Context,
        recipient: typing.Union[discord.Member, str],
        present_name: str,
        *,
        please=False
    ):
        """Underlying logic for `@santa give`, `@santa please give`
            and `@santa gimme`

        Args:
            ctx (discord.ext.commands.Context): [description]
            recipient (typing.Union[discord.Member, str]): [description]
            present_name (str): [description]
            please (bool, optional): [description]. Defaults to False.
        """
        invoking_user = self.bot.db.get_or_create(User, id=ctx.author.id)
        server = Server.get(id=ctx.guild.id)
        grinch = None
        grinch_visit = False

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
        else:
            grinch = GrinchManager(server.webhook_url)

        # Let the User know we're doing something if this takes a while
        await ctx.trigger_typing()

        # Send a present from one User to another
        if isinstance(recipient, discord.Member):
            if recipient.id == invoking_user.id:
                await ctx.send('Nice try {invoking_user.mention}...')
                return

            cooldown = invoking_user.check_cooldown(sending_gift=True)
            if cooldown:
                delay = self.__to_minutes(cooldown)

                await ctx.send(
                    "I'm sorry {0}, but you need to wait **{1}** minutes "
                    "before you can send another gift."
                    .format(ctx.author.mention, delay)
                )

                return

            # Send a present. 0% chance of the Grinch showing up.
            self.__send_present(
                invoking_user, recipient, server, present_name, please
            )

            await ctx.send(
                'Ho ho ho {0}, check under your tree for {1} from {2}!'
                .format(recipient.mention, present_name, ctx.author.mention)
            )

            # Our gifting work here is done (no Grinch for sent gifts)
            return

        # Send a present to the user who asked for one
        cooldown = invoking_user.check_cooldown()
        if cooldown:
            delay = self.__to_minutes(cooldown)
            print(f'> delay is {delay}')
            minute_s = 'minute' if delay == 1 else 'minutes'

            # No longer punishing the user with a cooldown reset if they
            # don't say please.
            await ctx.send(
                "Sorry, {0}, but you have to chill with the presents. "
                "Wait another **{1} {2}** and I'll give you another hit."
                .format(ctx.author.mention, delay, minute_s)
            )

            return

        # Cache the user's present count because it might get reset by
        # __give_present
        tmp_present_count = invoking_user.owned_present_count
        # Give the user the present and see if the Grinch steals their presents
        stolen = self.__give_present(
            invoking_user,
            server,
            present_name,
            please=please
        )

        # Santa gave us our Present and we avoided the Grinch!
        if not stolen:
            await ctx.send(
                'Ho ho ho {0}! Check under your tree for {1}!'
                .format(ctx.author.mention, present_name)
            )
            return

        # Gotta let the user know we stole their presents
        just_stolen = '**{0}** {1}'.format(
            tmp_present_count,
            'present' if tmp_present_count == 1 else 'presents'
        )

        grinch.send_message(
            'Heh heh heh... I just stole {0} from you, {1}!\n'
            .format(just_stolen, ctx.author.mention),
            'That makes it **{0}** so far!\n'
            .format(invoking_user.stolen_present_count),
            'https://i.imgur.com/iqEeKrF.jpg'
        )

        await ctx.send('Ah god damn it. He did it again.')

    # -------------------------------------------------------------------------
    # __give_present() handles the logic for a User who asked for a present
    # -------------------------------------------------------------------------
    def __give_present(
        self,
        invoking_user: discord.Member,
        server: Server,
        present_name: str,
        *,
        please=False
    ) -> bool:
        """Give a present to a user who asked for one, then try to steal it.

        Args:
            invoking_user (discord.Member): Who asked for the present?
            server (Server): The parent Server of the present.
            present_name (str): The name of the present.
            please (bool, optional): Did they say please? Defaults to False.

        Returns:
            bool: Whether the Grinch stole their presents.
        """
        present = Present(
            name=present_name,
            owner=invoking_user,
            server=server,
            please=please
        )

        invoking_user.increment_owned_presents()

        result = invoking_user.try_steal_presents()

        self.bot.db.commit()
        return result

    # -------------------------------------------------------------------------
    # __send_present() handles the logic for sending gifts from User to User
    # -------------------------------------------------------------------------
    def __send_present(
        self,
        invoking_user: discord.Member,
        recipient: discord.Member,
        server: Server,
        present_name: str,
        please=False
    ):
        """One user sends a present to another.

        Args:
            invoking_user (discord.Member): Who sent the gift.
            recipient (discord.Member): Who the gift is for.
            server (Server): The parent Server of the present.
            present_name (str): The name of the gift.
            please (bool, optional): The magic word. Defaults to False.
        """
        recipient = self.bot.db.get_or_create(User, id=recipient.id)

        present = Present(
            name=present_name,
            owner=recipient,
            gifter=invoking_user,
            server=server,
            please=please
        )

        recipient.increment_owned_presents()
        invoking_user.increment_gifted_presents()

        self.bot.db.commit()

    # -------------------------------------------------------------------------
    # __to_minutes() is just `math.ciel()` with no `import math`
    # -------------------------------------------------------------------------
    def __to_minutes(self, td) -> int:
        """Hack to round up int conversion without importing math.ceil

        Args:
            td (datetime.timedelta): The timedelta remaining

        Returns:
            int: The number of minutes (rounded up)
        """
        return int(ceil(td.total_seconds() / 60))


def setup(bot):
    bot.add_cog(Give(bot))
