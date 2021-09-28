import typing
import argparse
import telethon
from t2p.tasks.task import Tasker, TaskerError

from t2p.logger import logger

logger = logger.getChild('search_nearby_ones')


class NearbyOnesSeacher(Tasker):
    command = 'nearby_ones'

    def __init__(self) -> None:
        Tasker.__init__(self, 'search_nearby_ones')

    @classmethod
    def prepare(cls, parser: argparse._SubParsersAction):
        argparser_subparser = parser.add_parser(cls.command)
        argparser_subparser.add_argument(
            '-lat',
            required=True,
            type=float,
            dest='latitude',
            help='set the latitude'
        )
        argparser_subparser.add_argument(
            '-long',
            required=True,
            type=float,
            dest='longitude',
            help='set the longitude'
        )
        argparser_subparser.add_argument(
            '--users',
            action='store_true',
            dest='onlyusers',
            help='set only users'
        )
        argparser_subparser.add_argument(
            '--chats',
            action='store_true',
            dest='onlychats',
            help='set only chats'
        )

    def preload(self) -> None:
        if not self.args:
            logger.critical('The `args` is not redefined')
            raise TaskerError('Not defined arguments')

        if not hasattr(self.args, 'latitude') or not self.args.latitude:
            logger.critical('No given latitude')
            raise TaskerError('Missing argument "latitude"')

        if not hasattr(self.args, 'longitude') or not self.args.longitude:
            logger.critical('No given longitude')
            raise TaskerError('Missing argument "longitude"')

    async def start(self, client: telethon.TelegramClient) -> None:
        latitude: int = self.args.latitude
        longitude: int = self.args.longitude
        onlyusers: bool = self.args.onlyusers
        onlychats: bool = self.args.onlychats

        if onlyusers is False and onlychats is False:
            onlyusers = True
            onlychats = True

        logger.debug(f'latitude = {latitude} & longitude = {longitude}')

        # Build the function
        geo_located = telethon.functions.contacts.GetLocatedRequest(
            geo_point=telethon.types.InputGeoPoint(
                lat=latitude,
                long=longitude,
            )
        )
        result = await client(geo_located)
        result = typing.cast('telethon.types.Updates', result)

        if onlyusers:
            for user in result.users:
                user = typing.cast('telethon.types.User', user)
                # Get full name
                first_name = typing.cast(str, user.first_name)
                last_name = typing.cast(str, user.last_name)
                full_name = f'{first_name} {last_name}'
                full_name = full_name.strip()
                # Get username if exists
                username = user.username if user.username else 'username'
                print(f'({user.id}) - {full_name} @{username}')
            print()

        if onlychats:
            for chat in result.chats:
                chat = typing.cast('telethon.types.Chat', chat)
                print(
                    f'({chat.id}) - {chat.title} [{chat.participants_count}]')
            print()

    def end(self) -> None:
        return super().end()
