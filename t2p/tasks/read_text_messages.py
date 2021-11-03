import os
import asyncio
import argparse
import telethon
from typing import Optional
from telethon.events.newmessage import NewMessage
from t2p.tasks.task import Tasker, TaskerError

from t2p.logger import logger

logger = logger.getChild('read_text_messages')


class TextMessage(Tasker):
    command = 'text_messages'

    def __init__(self) -> None:
        Tasker.__init__(self, 'read_text_messages')
        self.event_new_message = NewMessage(outgoing=False)
        self.event_done = asyncio.Event()
        self.task: Optional[asyncio.Task] = None

    @classmethod
    def prepare(cls, parser: argparse._SubParsersAction):
        logger.debug('prepare argument parser')
        argparser_subparser = parser.add_parser(cls.command)
        argparser_subparser.add_argument(
            '--once',
            dest='once',
            action='store_true',
            help='Read a message and exit',
        )
        argparser_subparser.add_argument(
            '-SN',
            '--service-notifications',
            dest='sn',
            action='store_true',
            help='Read only messages from the service notifications',
        )
        argparser_subparser.add_argument(
            '--user-id',
            dest='user_id',
            type=int,
            nargs='?',
            help='Set the user id to filter the messages',
        )
        argparser_subparser.add_argument(
            '--chat-id',
            dest='chat_id',
            type=int,
            nargs='?',
            help='Set the chat id to filter the messages',
        )
        argparser_subparser.add_argument(
            '--channel-id',
            dest='channel_id',
            type=int,
            nargs='?',
            help='Set the channel id to filter the messages',
        )

    def preload(self) -> None:
        """Checks the values needed.

        To read text messages any of the values `sn`, `chat_id`, `channel_id`,
        and `user_id` must be defined.

        Raises:
            TaskerError - If data is missing.
        """
        logger.debug(f'preload: {self.args}')
        if not self.args:
            logger.critical('The `args` is not redefined')
            raise TaskerError('Not defined arguments')
        no_arguments = True
        if hasattr(self.args, 'sn') and self.args.sn:
            no_arguments = False
        if hasattr(self.args, 'chat_id') and self.args.chat_id:
            no_arguments = False
        if hasattr(self.args, 'user_id') and self.args.user_id:
            no_arguments = False
        if hasattr(self.args, 'channel_id') and self.args.channel_id:
            no_arguments = False
        if no_arguments:
            logger.critical('No given argument')
            raise TaskerError('Missing argument(s)')

    async def start(self, client: telethon.TelegramClient) -> None:
        """Read text messages.

        Args:
            client (:telethon:`telethon.TelegramClient`):
                The Telegram client object.
        """
        logger.debug('start')
        logger.debug(f'once = {self.args.once}')
        if self.args.sn:
            logger.debug(f'filter to service notifications')
        if self.args.user_id:
            logger.debug(f'user_id = {self.args.user_id}')
        if self.args.chat_id:
            logger.debug(f'chat_id = {self.args.chat_id}')
        if self.args.channel_id:
            logger.debug(f'channel_id = {self.args.channel_id}')
        client.on(self.event_new_message)(self.handler)
        logger.debug('registered handler')
        coro = client.run_until_disconnected()
        if coro is None:
            logger.warn('No coroutine found')
            raise Exception('No coroutine found')
        self.task = asyncio.create_task(coro)
        await self.event_done.wait()
        logger.debug('stopped client')

    def end(self) -> None:
        if self.task and not self.task.done:
            logger.info('end task')
            self.task.cancel()
        logger.debug('end')

    async def handler(self, event: NewMessage.Event):
        w, h = os.get_terminal_size()
        if self.args.sn or self.args.user_id:
            if not isinstance(event.from_id, telethon.tl.types.PeerUser):
                return
            # Read from service notifications or from requested user id
            user_id = 777000 if self.args.sn else self.args.user_id
            if event.from_id.user_id == user_id:
                print('user:', event.from_id, event.message.message)
                print('-'*w)
                # Check if `once` is True to stop this
                if self.args.once:
                    self.event_done.set()
        elif self.args.chat_id:
            if not isinstance(event.peer_id, telethon.tl.types.PeerChat):
                return
            if event.peer_id.chat_id == self.args.chat_id:
                print('chat:', event.peer_id, event.message.message)
                print('-'*w)
                # Check if `once` is True to stop this
                if self.args.once:
                    self.event_done.set()
        elif self.args.channel_id:
            if not isinstance(event.peer_id, telethon.tl.types.PeerChannel):
                return
            if event.peer_id.channel_id == self.args.channel_id:
                if self.args.user_id:
                    if event.from_id.user_id != self.args.user_id:
                        return
                print('channel:', event.peer_id, event.message.message)
                print('-'*w)
                # Check if `once` is True to stop this
                if self.args.once:
                    self.event_done.set()
