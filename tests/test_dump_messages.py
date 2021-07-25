import argparse
import asyncio

import pytest

import telethon
from telethon.helpers import TotalList

from t2p.tasks.task import TaskerError
from t2p.tasks.dump_messages import MessagesDumper

TOTAL = 4


class FakeObject(object):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)


async def fake_get_messages(self, client) -> list:
    message_list = [
        FakeObject(
            message='message text #1',
            id=1,
            reply_to=None,
            from_id=telethon.types.PeerChat(1000)
        ),
        FakeObject(
            message='message text #2 replies to #1',
            id=2,
            reply_to=FakeObject(reply_to_msg_id=1),
            from_id=telethon.types.PeerChannel(2000)
        ),
        FakeObject(
            message='message text #3',
            id=3,
            reply_to=None,
            from_id=telethon.types.PeerUser(3000)
        ),
        FakeObject(
            message='message text #4 replies to #1 again',
            id=4,
            reply_to=FakeObject(reply_to_msg_id=1),
            from_id=None,
        ),
    ]
    total_list = TotalList(message_list)
    total_list.total = TOTAL
    return total_list


@pytest.fixture
def dumped_messages(monkeypatch):
    monkeypatch.setattr(MessagesDumper, '_get_messages', fake_get_messages)
    return MessagesDumper()


def test_no_args(dumped_messages):
    with pytest.raises(TaskerError) as e:
        dumped_messages.preload()
        assert 'Not defined arguments' in str(e.value)


def test_no_datafilename(dumped_messages):
    dumped_messages.args = argparse.Namespace()
    with pytest.raises(TaskerError) as e:
        dumped_messages.preload()
        assert 'Missing argument' in str(e.value)


def test_no_target(dumped_messages):
    dumped_messages.args = argparse.Namespace(datafilename=True)
    with pytest.raises(TaskerError) as e:
        dumped_messages.preload()
        assert 'Missing argument' in str(e.value)


def test_full_preload(dumped_messages, tmpdir):
    datafilename = f'{tmpdir}/data.json'

    dumped_messages.args = argparse.Namespace(
        datafilename=datafilename,
        target='channel',
    )
    dumped_messages.preload()

    with open(datafilename, 'r') as file:
        assert file.read() == '{}'

    assert 'messages' in dumped_messages.data
    assert dumped_messages.last_mid == 1  # default
    assert dumped_messages.data['messages'] == {}


def test_full_dump_messages(dumped_messages, tmpdir):
    datafilename = f'{tmpdir}/data.json'

    dumped_messages.args = argparse.Namespace(
        datafilename=datafilename,
        target='channel',
    )
    dumped_messages.preload()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(dumped_messages.start(None))

    # TODO: should it be total_messages?
    assert dumped_messages.data['total_message'] == TOTAL

    messages = dumped_messages.data['messages']

    assert messages[1]['message'] == 'message text #1'
    assert messages[1]['peer_id'] == 1000
    assert messages[1]['type_peer'] == 'chat'
    assert messages[1]['reply_to'] == 0

    assert messages[2]['message'] == 'message text #2 replies to #1'
    assert messages[2]['peer_id'] == 2000
    assert messages[2]['type_peer'] == 'channel'
    assert messages[2]['reply_to'] == 1

    assert messages[3]['message'] == 'message text #3'
    assert messages[3]['peer_id'] == 3000
    assert messages[3]['type_peer'] == 'user'
    assert messages[3]['reply_to'] == 0

    assert messages[4]['message'] == 'message text #4 replies to #1 again'
    assert messages[4]['peer_id'] == 0
    assert messages[4]['type_peer'] == 'anonymous'
    assert messages[4]['reply_to'] == 1

    dumped_messages.end()

    with open(datafilename, 'r') as file:
        assert file.read() != '{}'
