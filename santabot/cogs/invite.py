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
        await ctx.send(
            "This bot was made by and is hosted by "
            "the Podcast About List Code Monkeys\n"
            "Check out the GitHub repo here: "
            "https://github.com/Podcast-About-List/santa\n"
            "Join the Podcast About List discord here: "
            "https://podaboutli.st/discord"
        )


def setup(bot):

    bot.add_cog(Invite(bot))
