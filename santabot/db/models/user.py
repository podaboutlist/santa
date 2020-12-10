from pony import orm
from datetime import datetime, timedelta
from ._base import db


class User(db.Entity):
    id = orm.PrimaryKey(int, size=64)
    owned_presents = orm.Set('Present', reverse='owner')
    gifted_presents = orm.Set('Present', reverse='gifter')
    # We cache owned_present_count and gifted_present_count so their values
    # aren't calculated every time statistics are requested.
    #
    # If we wanted to hugely over-enigeer this, we could cache these values in
    # something like Redis. lol. -Ralph
    owned_present_count = orm.Required(int, default=0, min=0)
    gifted_present_count = orm.Required(int, default=0, min=0)
    stolen_present_count = orm.Required(int, default=0, min=0)
    grinch_visit_count = orm.Required(int, default=0, min=0)

    last_gift_sent_datetime = orm.Required(
        datetime,
        default=datetime(year=2001, month=9, day=11, hour=8, minute=46)
    )
    last_gift_received_datetime = orm.Required(
        datetime,
        default=datetime(year=2013, month=4, day=15, hour=2, minute=50)
    )

    def get_stats(self):
        return
        self.owned_present_count,
        self.stolen_present_count,
        self.gifted_present_count,
        self.grinch_visit_count,
        self.gifted_presents,
        self.owned_presents,
        self.last_gift_sent_datetime,
        self.last_gift_received_datetime,
        "Ready for presents" if self.last_gift_datetime < datetime.now() - \
            timedelta(hours=1) else "Santa needs a break from yo needy ass"
