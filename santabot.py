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

from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
from pony import orm
from psycopg2 import OperationalError
from santabot.db import db


load_dotenv()

cogs = ['give', 'grinch', 'invite', 'stats']
santa = commands.Bot(
    command_prefix=commands.when_mentioned,
    owner_id=getenv('BOT_OWNER_ID')
)
santa.db = db


@santa.event
async def on_ready():
    print('> Santa Bot is online!')


if __name__ == '__main__':
    print('> Starting Santa Bot...')

    bot_token = getenv('BOT_TOKEN')
    if not bot_token:
        raise Exception(
            'Error: Expected a BOT_TOKEN, got {0}. Did you set up .env?'
            .format(bot_token)
        )

    use_sqlite = getenv('USE_SQLITE')
    sql_debug = getenv('SQL_DEBUG', False)

    orm.set_sql_debug(sql_debug)

    print('> Initialising database connection...')
    if use_sqlite.lower() == 'true':  # No easy way to convert str to bool :/
        print('> Using SQLite DB for testing.')
        santa.db.bind(
            provider='sqlite',
            filename='santabot.db',
            create_db=True
        )
    else:
        print('> Using PostgreSQL DB.')
        db_host = getenv('DB_HOST', default='127.0.0.1')
        db_port = getenv('DB_PORT', default='5432')
        db_name = getenv('DB_NAME')
        db_user = getenv('DB_USER')
        db_pass = getenv('DB_PASS')
        db_table_prefix = getenv('DB_TABLE_PREFIX')

        try:
            santa.db.bind(
                provider='postgres',
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_pass,
                database=db_name
            )
        except OperationalError as e:
            print('> Error connecting to the PostgreSQL database:')
            raise e

    print('> Generating database mapping...')
    santa.db.generate_mapping(create_tables=True)

    print('> Loading cogs...')
    for cog in cogs:
        cog = 'santabot.cogs.{0}'.format(cog)

        # TODO: Error handling when loading cogs
        santa.load_extension(cog)
        print('> Loaded cog ', cog)

    print('> Logging into Discord...')
    santa.run(bot_token)
