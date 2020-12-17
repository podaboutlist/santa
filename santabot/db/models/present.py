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
