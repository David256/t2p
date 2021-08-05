import os
import re

import telethon
from .task import Tasker, TaskerError

from ..logger import logger

logger = logger.getChild('send_voicenotes')


class VoiceNotesSender(Tasker):
    def __init__(self) -> None:
        Tasker.__init__(self, 'send_voicenotes')

    def preload(self) -> None:
        """Checks the values needed.
        
        To send voice notes is needed the value `target` that is the chat where
        the voice note will be sent. The value `filename` is needed too.

        Raises:
            TaskerError - If data is missing.
        """
        if not self.args:
            logger.critical('The `args` is not redefined')
            raise TaskerError('Not defined arguments')

        if not hasattr(self.args, 'filename') \
                or not self.args.filename:
            logger.critical('No voice note file given: filename')
            raise TaskerError('Missing argument "filename"')

        if not hasattr(self.args, 'target') or not self.args.target:
            logger.critical('No target given')
            raise TaskerError('Missing argument "target"')

        if not os.path.exists(self.args.filename):
            raise TaskerError('File given does not exist')
        logger.debug(f'filename is {self.args.filename}')

    async def start(self, client: telethon.TelegramClient) -> None:
        """Send the voice note.
        
        Args:
            client (:telethon:`telethon.TelegramClient`):
                The Telegram client object.
        """
        target = self.args.target

        if re.match(r'^-?\d+$', target):
            target = int(target, 10)
            logger.debug(f'The target is converted to integer: {target}')

        logger.info(f'Sending {self.args.filename}...')

        peer = await client.get_entity(target)
        logger.debug(peer)

        await client.send_file(
            peer,
            self.args.filename,
            voice_note=True,
        )

    def end(self) -> None:
        """Do nothing"""
        logger.info('Voice note sent.')