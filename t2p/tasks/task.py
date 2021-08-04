import telethon


class TaskerError(Exception):
    pass


class Tasker(object):
    def __init__(self, task_name: str) -> None:
        """Constructs a Tasker.

        Args:
            task_name (str): The name of the task.
        """
        self.name = task_name
        self.args = None

    def preload(self) -> None:
        """Method called before of starting the doing of the task.

        Generally, this method checks the dependencies and the values needed.

        Raises:
            TaskerError - when missing data.
        """
        pass

    async def start(self, client: telethon.TelegramClient) -> None:
        """Start the task.

        Args:
            client (:telethon:`telethon.TelegramClient`):
                The Telegram client object.
        """
        pass

    def end(self) -> None:
        """Does the finishing works."""
        pass
