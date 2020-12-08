#!/usr/bin/env python3

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

import json
from discord.ext import commands
# from pony import orm


# cogs = ['santabot.cogs.give', 'santabot.cogs.global', 'santabot.cogs.help',
#        'santabot.cogs.invite', 'santabot.cogs.my']
cogs = ['santabot.cogs.give']


def load_config_file(filename):
    # TODO: try/except for when the file is missing
    with(open('config/config.json', 'r')) as cfg_file:
        return json.load(cfg_file)


santa = commands.Bot(command_prefix=commands.when_mentioned)


@santa.event
async def on_ready():
    print('> Santa Bot is online!')


if __name__ == '__main__':
    print('> Loading Santa Bot config from file...')
    cfg = load_config_file('config/config.json')
    bot_token = cfg['bot']['token']

    print('> Loading cogs...')
    for cog in cogs:
        # TODO: Error handling when loading cogs
        santa.load_extension(cog)
        print('> Loaded cog ', cog)

    print('> Logging into Discord...')
    santa.run(bot_token)
