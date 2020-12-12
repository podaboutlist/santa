from pony import orm
from datetime import datetime, timedelta
from ._base import db
from .user import User


class Present(db.Entity):
    id = orm.PrimaryKey(int, size=64, auto=True)
    name = orm.Required(str)
    owner = orm.Required(User)
    gifter = orm.Optional(User)
    stolen = orm.Required(bool, default=False)
    please = orm.Required(bool, default=False)
    date_received = orm.Required(datetime, default=datetime.now())
    date_stolen = orm.Optional(datetime)



    @orm.db_session
    def calculate_global_presents(self) -> int:
        return db.count(p for p in Present)


    @orm.db_session
    def calculate_global_steals(self) -> int:
        return db.count(p for p in Present and p.stolen)