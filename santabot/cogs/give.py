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

    # FIXME: If both of these decorators are present, things don't work. If
    #        db_session() is added first, Discord.py doesn't register the
    #        command. If db_session() is added second, we get
    #        TypeError('Callback must be a coroutine.')

    # @orm.db_session()
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
            recipient (typing.Union[discord.Member, str]): Either the recipient
                of the present (a Member), or the first word of the Present.
            *args: Words describing the Present.
        """
        is_grinch_visit = False
        if not isinstance(recipient, discord.Member):
            # FIXME: I just hardcoded chance to 50% for testing. Need to
            #        implement a better system (see docs/DESIGN.md).
            is_grinch_visit = bool(randint(0, 1))

        if not is_grinch_visit:
            await ctx.trigger_typing()

        with orm.db_session:
            user = User.get(id=ctx.author.id) or User(id=ctx.author.id)
            server = Server.get(id=ctx.guild.id)

            if (not server) or (not server.webhook_url):
                await ctx.send(
                    '(error) No Webhook found for this server.\n'
                    'Please ask an admin to use `@santa grinch summon`.'
                )
                return

            giftee = None
            present = None

            if isinstance(recipient, discord.Member):
                giftee = User.get(id=recipient.id) or User(id=recipient.id)
                present = Present(
                    name=present_name,
                    owner=giftee,
                    gifter=user
                )
                giftee.increment_owned_presents()
                user.increment_gifted_presents()
            else:
                present = Present(
                    name=present_name,
                    owner=user
                )
                user.increment_owned_presents()

            if is_grinch_visit:
                grinch = GrinchManager(server.webhook_url)
                grinch.send_message(
                    # FIXME: Change statement to singular if only 1 present.
                    'Heh heh heh... I just stole {0} presents from you, {1}!\n'
                    .format(user.owned_present_count, ctx.author.mention),
                    # FIXME: Don't hardcode these images?
                    # TODO: Make some custom imagery for the repo.
                    'https://i.imgur.com/iqEeKrF.jpg'
                )

                user.steal_presents()
                return

            if giftee:
                await ctx.send(
                    'Ho ho ho {0}, check under your tree for {1} from {2}!'
                    .format(
                        recipient.mention,
                        present_name,
                        ctx.author.mention
                    )
                )
            else:
                await ctx.send(
                    'Ho ho ho! Check under your tree for {0}!'
                    .format(present_name)
                )

    @commands.command()
    async def please(
        self,
        ctx: discord.ext.commands.Context,
        _: str,
        recipient: typing.Union[discord.Member, str],
        *,
        args: str
    ):
        """Command for pleasantly asking for a present.

        Args:
            ctx (discord.ext.commands.Context): Discord.py command context.
            _ ([type]): The `give` prefix. Not used.
            recipient (typing.Union[discord.Member, str]): Either the recipient
                of the present (a Member), or the first word of the Present.
            *args: Words describing the Present.
        """
        await ctx.channel.trigger_typing()

        await self.give(ctx, recipient, args)
        await ctx.send('Thank you for saying please!')


def setup(bot):
    bot.add_cog(Give(bot))
