from datetime import datetime
from pony import orm
from ._base import db
from .server import Server
from .user import User


class Present(db.Entity):
    id = orm.PrimaryKey(int, size=64, auto=True)
    server = orm.Required(Server)
    name = orm.Required(str)
    owner = orm.Required(User)
    gifter = orm.Optional(User)
    stolen = orm.Required(bool, default=False)
    please = orm.Required(bool, default=False)
    date_received = orm.Required(datetime, default=datetime.now(), precision=6)
    date_stolen = orm.Optional(datetime)

    @staticmethod
    @orm.db_session
    def calculate_all_time_presents() -> int:
        """Calculate all time number of presents distributed.

        Returns:
            int: All time number of presents distributed.
        """
        return db.select(lambda p: True).count()

    @staticmethod
    @orm.db_session
    def calculate_active_presents() -> int:
        """Calculate how many presents are currently not 'stolen'

        Returns:
            int: Number of non-stolen presents.
        """
        return db.select(lambda p: not p.stolen).count()

    @staticmethod
    @orm.db_session
    def calculate_all_stolen_presents() -> int:
        """Calculate how many presents are currently 'stolen'

        Returns:
            int: Number of stolen presents.
        """
        return db.select(lambda p: p.stolen).count()

    @staticmethod
    @orm.db_session
    def calculate_all_self_presents() -> int:
        """Calculate how many presents were given to a user by themselves

        Returns:
            int: Number of self-gifted presents.
        """
        return db.select(lambda p: not p.stolen and p.owner.id == p.gifter.id).count()

    @staticmethod
    @orm.db_session
    def calculate_please() -> int:
        """Calculate how many presents were given to a user by themselves

        Returns:
            int: Number of self-gifted presents.
        """
        return db.select(lambda p: p.please).count()

    @orm.db_session
    def steal(self, timestamp=None) -> bool:
        """Marks this present as stolen by the Grinch

        Args:
            timestamp (datetime, optional): The datetime to assign to
                self.date_stolen. Defaults to datetime.now()

        Returns:
            bool: False if the present was previously stolen, otherwise True.
        """
        if self.stolen:
            return False

        self.stolen = True
        self.date_stolen = timestamp if timestamp else datetime.now()

        return True
