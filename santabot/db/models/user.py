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

    @orm.db_session
    def steal_presents(self):
        # Import statement placed here to avoid circular imports
        from .present import Present

        presents = Present.select(
            lambda p: (p.owner.id == self.id and p.stolen is False)
        )

        for present in presents:
            present.stolen = True
            present.date_stolen = datetime.now()

            self.stolen_present_count += 1

        self.owned_present_count = 0
        self.grinch_visit_count += 1

    @orm.db_session
    def increment_owned_presents(self, amount=1):
        self.owned_present_count += amount

    @orm.db_session
    def increment_gifted_presents(self, amount=1):
        self.gifted_present_count += amount

    @orm.db_session
    def calculate_owned_presents(self, update_cache=True) -> int:
        # FIXME: Find a way to refactor out this import line at the top
        #        of every function that accesses another model
        from .present import Present

        # TODO: Fin a way to simply count elements rather than loading them
        #       all into a list and running len()
        presents = Present.select(
            lambda p: (p.owner.id == self.id and p.stolen is False)
        )

        pc = len(presents)

        if update_owned:
            self.owned_present_count = pc

        return pc

    @orm.db_session
    def calculate_stolen(self, update_cache=True) -> int:
        pass

    @orm.db_session
    def list_presents(self, *args, count=10):
        pass
