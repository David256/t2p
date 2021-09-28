import os
import json

import telethon

from t2p.tasks.task import Tasker, TaskerError

from t2p.logger import logger

logger = logger.getChild('dump_messages')


class MessagesDumper(Tasker):
    def __init__(self) -> None:
        Tasker.__init__(self, 'dump_messages')
        self.data: dict = {}
        self.last_mid = 1

    async def _get_messages(self, client: telethon.TelegramClient):
        result = await client.get_messages(
            entity=self.args.target,
            offset_id=self.last_mid,
            reverse=True
        )
        return result

    def preload(self) -> None:
        """Checks the values needed.

        To the task of dumping messages it is needed the filename to save the
        gotten data. This value is in `datafilename`. Also, the value `target`
        sets the target peer, channel ID, group ID or username.

        If a data file exists, then it is loaded. If the value of `last_mid`
        (that means last message ID) is set, then the messages will be
        requested from last message read.

        Raises:
            TaskerError - If data is missing.
        """
        if not self.args:
            logger.critical('The `args` is not redefined')
            raise TaskerError('Not defined arguments')

        if not hasattr(self.args, 'datafilename') \
                or not self.args.datafilename:
            logger.critical('No file given to write data: datafilename')
            raise TaskerError('Missing argument "datafilename"')

        if not hasattr(self.args, 'target') or not self.args.target:
            logger.critical('No target given')
            raise TaskerError('Missing argument "target"')

        # Load last data or create empty data file
        if not os.path.exists(self.args.datafilename):
            with open(self.args.datafilename, 'w') as file:
                json.dump({}, file)
                logger.info('Create empty file.')

        # Load data
        with open(self.args.datafilename, 'r') as file:
            self.data = json.load(file)
            self.last_mid = self.data.get('last_mid', 1)
            logger.debug(f'Value of `last_mid` is {self.last_mid}')

        # Check JSON content
        if 'messages' not in self.data:
            self.data['messages'] = {}

        # Show stats in data
        logger.info(
            'There are %d messages saved.', len(self.data['messages']))
        logger.info('Last mID is %d.', self.last_mid)

    async def start(self, client: telethon.TelegramClient) -> None:
        """Requests messages from last message read or from the first message.

        The data to save will be:

        - Message ID.
        - Message text.
        - Author name.
        - Type of author. This can be `anonymous`, `user`, or `channel`.

        Args:
            client (:telethon:`telethon.TelegramClient`):
                The Telegram client object.
        """
        logger.debug(f'Target is {self.args.target}')
        result = await self._get_messages(client)

        # Show info
        logger.info('Total messages: %d.', result.total)
        logger.info('Read %d messages.', len(result))

        # Update total message count
        self.data['total_message'] = result.total

        for message in result:
            if message.message:
                peer_id = 'anonymous'
                type_peer = 'anonymous'
                if message.from_id:
                    if isinstance(message.from_id, telethon.types.PeerChat):
                        peer_id = message.from_id.chat_id
                        type_peer = 'chat'
                    elif isinstance(
                            message.from_id, telethon.types.PeerChannel):
                        peer_id = message.from_id.channel_id
                        type_peer = 'channel'
                    elif isinstance(message.from_id, telethon.types.PeerUser):
                        peer_id = message.from_id.user_id
                        type_peer = 'user'

                # Prepare info
                info = f'{message.id}: {peer_id}: "{message.message}"'
                if message.reply_to:
                    info += f' - reply to {message.reply_to.reply_to_msg_id}'
                logger.info(info)

                # Update data
                self.data['last_mid'] = message.id
                if message.id in self.data['messages']:
                    print(f'Message id {message.id} is saved already')
                else:
                    self.data['messages'][message.id] = {
                        'message': message.message,
                        'peer_id': 0 if peer_id == 'anonymous' else peer_id,
                        'type_peer': type_peer,
                        'reply_to': 0
                        if not message.reply_to
                        else message.reply_to.reply_to_msg_id
                    }

    def end(self) -> None:
        """Save dumped data to file."""
        with open(self.args.datafilename, 'w') as file:
            json.dump(self.data, file, indent=4)
        logger.info('Data saved in %s', self.args.datafilename)
