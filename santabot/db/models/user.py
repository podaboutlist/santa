from datetime import datetime, timedelta
from os import getenv
from pony import orm
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

    def get_stats(self):
        return
        self.owned_present_count,
        self.stolen_present_count,
        self.gifted_present_count,
        self.grinch_visit_count,
        self.gifted_presents,
        self.owned_presents

    @orm.db_session
    def __steal_presents(self):
        """Actually steal the user's presents.
           This function should only be called internally.
        """
        # Import statement placed here to avoid circular imports
        from .present import Present

        presents = Present.select(
            lambda p: (p.owner.id == self.id) and (p.stolen is False)
        )

        if not presents:
            return

        for present in presents:
            if present.steal():
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

        Args:
            please (bool, optional): [description]. Defaults to False.

        Returns:
            bool: Whether presents were stolen or not.
        """
        present_count = self.owned_present_count

        # if present_count < int(getenv('GRINCH_STEAL_THRESHOLD')):
        # return False

        random_int = randint(0, present_count)
        threshold = present_count ** (1 / 3)  # cube root

        # Being nice gets you places. Here, it gets you a slightly better
        # chance of not getting your presents swiped.
        if please:
            threshold = threshold * float(getenv('SAID_PLEASE_BONUS'))

        if random_int > int(threshold):
            self.__steal_presents()
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
        """Get a count of all presents in the database owned by this User
           in the database.

        Args:
            update_cache (bool, optional): Whether to update
                self.owned_present_count. Defaults to True.

        Returns:
            int: The number of presents this User owns
        """
        # FIXME: Find a way to refactor out this import line at the top
        #        of every function that accesses another model
        from .present import Present

        pc = Present.select(
            lambda p: p.owner.id == self.id and p.stolen is False
        ).count()

        if update_cache:
            self.owned_present_count = pc

        return pc

    @orm.db_session
    def calculate_stolen_presents(self, update_cache=True) -> int:
        """Iterate over this User's presents in the database and calculate how
           many are marked as stolen.

        Args:
            update_cache (bool, optional): Whether to update
                self.stolen_present_count. Defaults to True.

        Returns:
            int: The number of presents stolen from the User
        """
        # FIXME: Find a way to refactor out this import line at the top
        #        of every function that accesses another model
        from .present import Present

        sc = Present.select(
            lambda p: p.owner.id == self.id and p.stolen
        ).count()

        if update_cache:
            self.stolen_present_count = sc

        return sc

    @orm.db_session
    def list_presents(self, page=1):
        from .present import Present

        return Present.select(
            p for p in Present if p.owner.id == self.id
        ).order_by(
            orm.desc(Present.date_received)
        ).page(page)

    @orm.db_session
    def most_recent_present(self, *, is_gift=False, is_stolen=False):
        """Get the most recent present the user received

        Args:
            is_gift (bool, optional): Filter gifts vs presents the User
                asked for. Defaults to False.
            is_stolen (bool, optional): Filter gifts based on their 'stolen'
                status.

        Returns:
            Present: The most recent Present. Can be `None` if user has
                no presents.
        """
        from .present import Present

        presents = None

        if is_gift:
            presents = Present.select(
                lambda p: p.gifter.id == self.id and
                p.stolen == is_stolen
            )
        else:
            presents = Present.select(
                lambda p: p.owner.id == self.id and
                p.stolen == is_stolen
            )

        return presents.order_by(orm.desc(Present.date_received)).first()

    @orm.db_session
    def check_cooldown(self, *, sending_gift=False) -> bool:
        """Check to see if this User is on a Present giving cooldown

        Args:
            sending_gift (bool, optional): Which cooldown to check, gift
                requesting or gift sending. Defaults to False (requesting).

        Returns:
            (bool|float): False if the User is not on cooldown, otherwise
                the remaining seconds of the cooldown.
        """
        now = datetime.now()
        delay = None
        last_gift = None

        if sending_gift:
            delay = timedelta(minutes=int(getenv('GIFT_SEND_DELAY_MINUTES')))
        else:
            delay = timedelta(minutes=int(getenv('GIFT_ASK_DELAY_MINUTES')))

        last_gift = self.most_recent_present(is_gift=sending_gift)

        # If the user has no gifts
        if not last_gift:
            print('no last gift')
            return False

        last_gift = last_gift.date_received

        # Are we currently at a later time than the end of the cooldown?
        if now > last_gift + delay:
            return False
        else:
            # Do some funky casting stuff to get a timedelta
            return (last_gift + delay) - now
