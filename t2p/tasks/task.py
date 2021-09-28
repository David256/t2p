from abc import ABC, abstractmethod

import telethon
import argparse


class TaskerError(Exception):
    pass


class Tasker(ABC):
    def __init__(self, task_name: str) -> None:
        """Constructs a Tasker.

        Args:
            task_name (str): The name of the task.
        """
        self.name = task_name
        self.args = argparse.Namespace()

    @classmethod
    @abstractmethod
    def prepare(cls, parser: argparse._SubParsersAction):
        pass

    @abstractmethod
    def preload(self) -> None:
        """Method called before of starting the doing of the task.

        Generally, this method checks the dependencies and the values needed.

        Raises:
            TaskerError - when missing data.
        """
        pass

    @abstractmethod
    async def start(self, client: telethon.TelegramClient) -> None:
        """Start the task.

        Args:
            client (:telethon:`telethon.TelegramClient`):
                The Telegram client object.
        """
        pass

    @abstractmethod
    def end(self) -> None:
        """Does the finishing works."""
        pass
