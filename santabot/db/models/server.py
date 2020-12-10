from pony import orm
from datetime import datetime, timedelta
from ._base import db


class Server(db.Entity):
    id = orm.PrimaryKey(int, size=64)
    webhook_url = orm.Optional(str)
