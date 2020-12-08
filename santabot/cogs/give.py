import discord
import typing
from discord.ext import commands


class Give(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def give(self, ctx,
                   recipient: typing.Union[discord.Member, str], *args):
        if isinstance(recipient, discord.Member):
            await ctx.send(
                'Ho ho ho {0}, check under your tree for {1} from {2}'
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
        await self.give(ctx, recipient, *args)
        await ctx.send('Thank you for saying please!')


def setup(bot):
    bot.add_cog(Give(bot))
