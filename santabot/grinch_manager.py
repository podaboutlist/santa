import discord
from os import getenv
from typing import Union


class GrinchManager():
    """GrinchManager: Helper class for the Grinch webhook implementation.
    """
    def __init__(self, webhook_url: str):
        """Creates a Grinch from a Discord Webhook URL

        Args:
            webhook_url (str): The webhook URL.
        """
        # We create our own Webhook object from a URL instead of passing
        # objects around due to issues with synchronous vs asynchronous
        # webhook adapters.

        # TODO: Implement error handling
        self.webhook = discord.Webhook.from_url(
            webhook_url,
            adapter=discord.RequestsWebhookAdapter()
        )

        self.name = getenv('WEBHOOK_NAME')
        self.avatar_url = getenv('WEBHOOK_AVATAR_URL')

    def send_message(self, *message: str):
        """Sends a message as the Grinch using a webhook.

        Args:
            message (str): The message to send.
        """
        self.webhook.send(
            content=''.join(message),
            username=self.name,
            avatar_url=self.avatar_url
        )
