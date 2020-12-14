from pony import orm
from ._base import db


class Server(db.Entity):
    id = orm.PrimaryKey(int, size=64)
    channel_id = orm.Optional(int, size=64)
    webhook_url = orm.Optional(str)

    @orm.db_session
    def is_configured(self) -> bool:
        return (
            isinstance(self.channel_id, int) and
            isinstance(self.webhook_url, str)
        )

    @orm.db_session
    def add_webhook(self, *, channel_id: int, webhook_url: str):
        self.channel_id = channel_id
        self.webhook_url = webhook_url

    @orm.db_session
    def remove_webhook(self):
        self.channel_id = None
        self.webhook_url = ''
