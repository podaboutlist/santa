from pony import orm
from time import localtime
from ._base import db
from .user import User


class Present(db.Entity):
    id = orm.PrimaryKey(int, size=64, auto=True)
    name = orm.Required(str)
    owner = orm.Required(User)
    gifter = orm.Optional(User)
    stolen = orm.Required(bool, default=False)
    please = orm.Required(bool, default=False)
    date_received = orm.Required(datetime, default=localtime(), precision=6)
    __date_stolen = orm.Optional(datetime)

    @orm.db_session
    def calculate_all_time_presents(self) -> int:
        """Calculate all time number of presents distributed.

        Returns:
            int: All time number of presents distributed.
        """
        return db.count(p for p in Present)

    @orm.db_session
    def calculate_active_presents(self) -> int:
        """Calculate how many presents are currently not 'stolen'

        Returns:
            int: Number of non-stolen presents.
        """
        return db.count(
            lambda p: p.stolen is False
        )

    @orm.db_session
    def calculate_all_stolen_presents(self) -> int:
        return db.count(lambda p: p.stolen)

    @orm.db_session
    def steal(self, timestamp=None) -> bool:
        """Marks this present as stolen by the Grinch

        Args:
            timestamp (float, optional): Instead of localtime(), use this
                value (i.e. from time.time()). Defaults to None.

        Returns:
            bool: False if the present was previously stolen, otherwise True.
        """
        if self.stolen return False

        self.stolen = True
        self.__date_stolen = timestamp if timestamp else localtime()

        return True
