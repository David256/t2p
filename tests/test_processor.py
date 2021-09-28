import pytest

import asyncio

from t2p.tasks.task import Tasker
from t2p import TasksProcessor

times_called = 0


class FakeObject(object):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeTask(Tasker):
    def __init__(self, task_name: str) -> None:
        super().__init__(task_name)

    async def start(self, client) -> None:
        return await super().start(client)

    def preload(self) -> None:
        return super().preload()

    def end(self) -> None:
        return super().end()


def fake_create_client(self):
    self.client = FakeObject(loop=asyncio.get_event_loop())


def method_which_shall_not_be_called(self):
    pytest.fail('This method shall not be called')


async def coroutine_which_shall_not_be_called(self, client):
    pytest.fail('This corrutine shall not be called')


def sum_method(self):
    global times_called
    times_called += 1


async def sum_coroutine(self, client):
    sum_method(self)


@pytest.fixture
def processor(monkeypatch):
    monkeypatch.setattr(TasksProcessor, '_create_client', fake_create_client)

    tp = TasksProcessor(None)
    tp.taskers = []

    return tp


def test_without_matching(monkeypatch, processor):
    monkeypatch.setattr(FakeTask, 'preload', method_which_shall_not_be_called)
    monkeypatch.setattr(FakeTask, 'start', coroutine_which_shall_not_be_called)
    monkeypatch.setattr(FakeTask, 'end', method_which_shall_not_be_called)
    task1 = FakeTask('nothing')
    task2 = FakeTask('nothing')

    processor.taskers = [task1, task2]

    processor.run_task('thing', None)


def test_with_matching(monkeypatch, processor):
    monkeypatch.setattr(FakeTask, 'preload', sum_method)
    monkeypatch.setattr(FakeTask, 'start', sum_coroutine)
    monkeypatch.setattr(FakeTask, 'end', sum_method)
    task1 = FakeTask('thing')
    task2 = FakeTask('another')

    processor.taskers = [task1, task2]

    processor.run_task('thing', None)

    assert times_called == 3
