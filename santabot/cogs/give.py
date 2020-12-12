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
from ..db.models import Present, Server, User
from ..grinch_manager import GrinchManager


class Give(commands.Cog):
    """Parent class for commands that request presents.
    """

    def __init__(self, bot):
        self.bot = bot
        self.please = False

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
        with orm.db_session:
            await self.__do_gifting(ctx, recipient, present_name)

    @commands.command()
    async def please(
        self,
        ctx: discord.ext.commands.Context,
        _: str,  # give
        recipient: typing.Union[discord.Member, str],  # @user or 'me'
        *,
        present_name: str
    ):
        """Command for pleasantly asking for a present.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            _ (str): The `give` prefix. Not used.
            recipient (discord.Member or str]): Either the recipient of the
                present (a Member), or the first word of the Present.
            present_name (str): The name of the present.
        """
        with orm.db_session:
            await self.__do_gifting(ctx, recipient, present_name, please=True)

    async def __do_gifting(
        self,
        ctx: discord.ext.commands.Context,
        recipient: typing.Union[discord.Member, str],
        present_name: str,
        *,
        please=False
    ):
        """Underlying logic for `@santa give` and @santa please give`

        Args:
            ctx (discord.ext.commands.Context): [description]
            recipient (typing.Union[discord.Member, str]): [description]
            present_name (str): [description]
            please (bool, optional): [description]. Defaults to False.
        """
        # TODO: Make sure invoking_user isn't on cooldown from sending gifts.
        invoking_user = self.bot.db.get_or_create(User, id=ctx.author.id)
        # Are we giving another user a present?
        user_to_user = isinstance(recipient, discord.Member)
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

        if user_to_user:
            if invoking_user.check_send_timer():
                # Send a present. 0% chance of the Grinch showing up.
                self.__send_present(
                    invoking_user, recipient, present_name, please)

                await ctx.send(
                    'Ho ho ho {0}, check under your tree for {1} from {2}!'
                    .format(recipient.mention, present_name, ctx.author.mention)
                )

                # Our gifting work here is done (no Grinch for sent gifts)
                return

            else:
                await ctx.send(
                    "I'm sorry {0}, but you'll need to wait a little while "
                    "before sending another gift."
                    .format(ctx.author.mention)
                )

                return

        if invoking_user.check_receive_timer():
            tmp_present_count = invoking_user.owned_present_count

            # Give the User a present and check to see if the Grinch showed up.
            if self.__give_present(invoking_user, present_name, please=please):
                # FIXME: Change statement to singular if only 1 present.
                # FIXME: Don't hardcode attached images?
                # TODO:  Make some custom artwork for these messages.
                grinch.send_message(
                    'Heh heh heh... I just stole **{0}** {1} from you, {2}!\n'
                    .format(tmp_present_count,
                            "present" if tmp_present_count == 1 else "presents",
                            ctx.author.mention),
                    'That makes it **{0}** {1} stolen from you so far!\n'
                    .format(invoking_user.stolen_present_count,
                            "present" if invoking_user.stolen_present_count == 1 else "presents"),
                    'https://i.imgur.com/iqEeKrF.jpg'
                )

                await ctx.send('Ah god damn it. He did it again.')
                return

        else:
            if please:
                await ctx.send('Santa is busy delivering presents to the child soldiers of Uganda!\n'
                               'Please try again in **{0}** minutes.')
                .format(invoking_user.get_receive_time_remaining())

                return
            else:
                await ctx.send('https://i.imgur.com/0oh6ZML.png'
                               '**Your avarice has angered Santa.\n**'
                               '**You have been placed on the naughty list for the next {0} minutes**'
                               .format(int(getenv('WAIT_MINUTES')))
                               )
                invoking_user.reset_receive_timer()

                return

        # Santa gave us our Present and we avoided the Grinch!
        await ctx.send(
            'Ho ho ho {0}! Check under your tree for {1}!'
            .format(ctx.author.mention, present_name)
        )

    def __give_present(
        self,
        invoking_user: discord.Member,
        present_name: str,
        *,
        please=False
    ) -> bool:
        """Give a present to a user who asked for one, then try to steal it.

        Args:
            invoking_user (discord.Member): Who asked for the present
            present_name (str): The name of the present
            please (bool, optional): Did they say please? Defaults to False.

        Returns:
            bool: Whether the Grinch stole their presents.
        """
        present = Present(
            name=present_name,
            owner=invoking_user,
            please=please
        )

        invoking_user.increment_owned_presents()
        invoking_user.reset_receive_timer()

        return invoking_user.try_steal_presents()

    def __send_present(
        self,
        invoking_user: discord.Member,
        recipient: discord.Member,
        present_name: str,
        please=False
    ):
        """One user sends a present to another.

        Args:
            invoking_user (discord.Member): Who sent the gift.
            recipient (discord.Member): Who the gift is for.
            present_name (str): The name of the gift.
            please (bool, optional): The magic word. Defaults to False.
        """
        recipient = self.bot.db.get_or_create(User, id=recipient.id)

        present = Present(
            name=present_name,
            owner=recipient,
            gifter=invoking_user,
            please=please
        )

        recipient.increment_owned_presents()
        invoking_user.increment_gifted_presents()
        invoking_user.reset_send_timer()


def setup(bot):
    bot.add_cog(Give(bot))
