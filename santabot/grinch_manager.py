import discord
from typing import Union


class GrinchManager():
    """GrinchManager: Helper class for the Grinch webhook implementation.
    """
    def __init__(self,
                 webhook: Union[discord.Webhook, str],
                 name: str,
                 avatar_url: str):
        """Wrapper class for webhook logic that powers the Grinch's messages.

        Args:
            webhook (discord.Webhook): The Webhook for sending messages.
            name (str): The display name of the Webhook
            avatar_url (str): The URL of the Webhook's avatar.
        """
        # TODO: Persist webhook URL in the database, restore it when needed

        if isinstance(webhook, discord.Webhook):
            self.webhook = webhook
        else:
            self.webhook = discord.Webhook.from_url(
                webhook,
                adapter=discord.RequestsWebhookAdapter()
            )

        self.name = name
        self.avatar_url = avatar_url

    def send_message(self, message: str):
        """Sends a message as the Grinch using a webhook.

        Args:
            message (str): The message to send.
        """
        self.webhook.send(
            content=message,
            username=self.name,
            avatar_url=self.avatar_url
        )

    def die(self, killer: str):
        """Remove the Grinch webhook

        Args:
            killer (str): The user who killed the Grinch
        """
        self.webhook.delete(
            reason='{0} banished the Grinch'.format(killer)
        )
