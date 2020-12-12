from os import getenv
from pony import orm
from datetime import datetime, timedelta
from random import randint
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

    # The Grinch statistics 0_o
    max_present_count = orm.Required(int, default=0, min=0)
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
    def __steal_presents(self):
        """Actually steal the user's presents.
           This function should only be called internally.
        """
        # Import statement placed here to avoid circular imports
        from .present import Present

        presents = Present.select(
            lambda p: (p.owner.id == self.id and p.stolen is False)
        )

        for present in presents:
            present.stolen = True
            present.date_stolen = datetime.now()

            self.stolen_present_count += 1

        if self.owned_present_count > self.max_present_count:
            self.max_present_count = self.owned_present_count

        self.owned_present_count = 0
        self.grinch_visit_count += 1

    @orm.db_session
    def try_steal_presents(self, please=False) -> bool:
        """Attempt to steal the presents from this user. The chance of a steal
           is calculated with the formula

               rand(0, present_count) > cube_root(present_count) * please_bonus

        Returns:
            bool: Whether presents were stolen or not.
        """
        present_count = self.owned_present_count

        if present_count < int(getenv('GRINCH_STEAL_THRESHOLD')):
            return False

        random_int = randint(0, present_count)
        threshold = present_count ** (1/3)  # cube root

        # Being nice gets you places. Here, it gets you a slightly better
        # chance of not getting your presents swiped.
        if please:
            threshold = threshold * float(getenv('SAID_PLEASE_BONUS'))

        if random_int > int(threshold):
            self.steal_presents()
            return True

        return False

    @orm.db_session
    def increment_owned_presents(self, amount=1):
        self.owned_present_count += amount

    @orm.db_session
    def increment_gifted_presents(self, amount=1):
        self.gifted_present_count += amount

    @orm.db_session
    def calculate_owned_presents(self, update_cache=True) -> int:
        """Get

        Args:
            update_cache (bool, optional): [description]. Defaults to True.

        Returns:
            int: [description]
        """
        # FIXME: Find a way to refactor out this import line at the top
        #        of every function that accesses another model
        from .present import Present

        pc = db.count(p for p in Present if p.owner.id == self.id)

        if update_cache:
            self.owned_present_count = pc

        return pc

    @orm.db_session
    def calculate_stolen_presents(self, update_cache=True) -> int:
        # FIXME: Find a way to refactor out this import line at the top
        #        of every function that accesses another model
        from .present import Present

        sc = db.count(
            p for p in Present if (p.owner.id == self.id) and p.stolen
        )

        if update_cache:
            self.stolen_present_count = sc

        return sc

    @orm.db_session
    def list_presents(self, page=1):
        from .present import Present

        Present.select(
            p for p in Present if p.owner.id == self.id
        ).order_by(
            lambda p: desc(p.date_received)
        ).page(page)
