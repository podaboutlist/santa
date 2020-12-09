from discord import Webhook


class GrinchManager():
    """GrinchManager: Helper class for the Grinch webhook implementation.
    """
    def __init__(self, webhook: Webhook, name: str, avatar_url: str):
        """Wrapper class for webhook logic that powers the Grinch's messages.

        Args:
            webhook (Webhook): The Webhook for sending messages.
            name (str): The display name of the Webhook
            avatar_url (str): The URL of the Webhook's avatar.
        """
        # TODO: Persist webhook data in the database
        self.webhook = webhook
        self.name = name
        self.avatar_url = avatar_url

    async def send_message(self, message: str):
        """Sends a message as the Grinch using a webhook.

        Args:
            message (str): The message to send.
        """
        await self.webhook.send(
            content=message,
            username=self.name,
            avatar_url=self.avatar_url
        )

    async def die(self, killer: str):
        """Remove the Grinch webhook

        Args:
            killer (str): The user who killed the Grinch
        """
        await self.webhook.delete(
            reason='{0} banished the Grinch'.format(killer)
        )
