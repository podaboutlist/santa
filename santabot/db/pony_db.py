from pony.orm import *
from datetime import datetime, timedelta

db = Database()

# not sure how we want to set the db up
db.bind(provider='sqlite', filename=':memory:')


class User(db.Entity):
    id = PrimaryKey(int)
    presents = Set("Present")
    total_presents = Required(int, default=0, min=0)
    stolen_presents = Required(int, default=0, min=0)
    given_presents = Required(int, default=0, min=0)
    steal_count = Required(int, default=0, min=0)
    last_gift_datetime = Required(datetime, default=datetime(
        year=2001, month=9, day=11, hour=8, minute=46))

    def get_stats(self):
        return self.total_presents,
        self.stolen_presents,
        self.given_presents,
        self.total_snatches,
        self.given_presents,
        "Ready for presents" if self.last_gift_datetime < datetime.now() - \
            timedelta(hours=1) else "Santa needs a break from yo needy ass"


class Present(db.Entity):
    id = PrimaryKey(int)
    name = Required(str)
    owner = Required(User)
    gifter = Optional(int)
    stolen = Required(bool, default=False)
    please = Required(bool, default=False)
    date_received = Required(datetime, default=datetime.now())
    date_stolen = Optional(datetime)


class Server(db.Entity):
    id = PrimaryKey(int)
    webhook_url = (str)


db.generate_mapping(create_tables=True)


# test db
"""
with db_session:
    test = User(id=1)
    x = User.get(id=1)
    print(x.last_gift_datetime)
    xx = x.get_stats()
    print(xx) """
