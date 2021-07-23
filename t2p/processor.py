"""
Processor
=========

This module defines the class ``TasksProcessor`` which will process tasks.
"""

import locale

import telethon

from .version import __version__
from .logger import logger
from .tasks.task import Tasker, TaskerError
from .tasks.dump_messages import MessagesDumper

class TasksProcessor:
    """
    Processes tasks over a Telegram session.

    This class defines and starts a Telegram client taking information of parameter ``config``. Also, adds some taskers to be available. This taskers can be called using the method ``run_task``.
    """
    def __init__(self, config) -> None:
        """Initialize the TasksProcessor object.
        
        :param config: The configuration object to create and start the Telegram client.
        :type config: ConfigParser
        """
        self.config = config
        # Prepare parameters
        session = config['Access']['session']
        api_id = int(config['Access']['id'])
        api_hash = config['Access']['hash']
        timeout = int(config['Client'].get('timeout', 7000))
        device_model = config['Client'].get('device_model', 'Telegram Tasks Processor')
        lang_code = config['Client'].get('lang_code', locale.getlocale()[0])
        logger.debug('Set timeout to %d', timeout)
        logger.debug('Set device model to "%s"', device_model)
        logger.debug('Set lang code to %s', lang_code)
        # Create the Telegram client
        self.client = telethon.TelegramClient(
            session=session,
            api_id=api_id,
            api_hash=api_hash,
            timeout=timeout,
            device_model=device_model,
            lang_code=lang_code,
            app_version=__version__,
            auto_reconnect=True
        )

        # Start the client
        self.client.start(
            phone=config['User']['phone'],
            password=config['User'].get('password')
        )

        # Available task
        self.taskers = [
            MessagesDumper()
        ]

        logger.info('%d taskers loaded', len(self.taskers))
    
    def run_task(self, task_name: str, cli_args: object) -> None:
        """Finds a tasker what can do a task.

        This method filters the taskers by matching with the parameter ``task_name``, and start processing in four phases:
        #. Define the argument passed via CLI argument.
        #. Call the method preload.
        #. Call the method start and await Coroutine ending.
        #. Call the method end.

        :param task_name: The name of the task.
        :type task_name: str
        :param cli_args: The CLI arguments.
        :type cli_args: Namespace
        """
        logger.debug('find task by task name "%s"', task_name)
        # Find a tasker
        tasker:Tasker = None
        for _tasker in self.taskers:
            if _tasker.name == task_name:
                tasker = _tasker
                break

        if not tasker:
            logger.error('No taskers registered')
            return

        # Update the cli arguments
        tasker.args = cli_args

        try:
            # Preload
            logger.info('Calling preload method')
            tasker.preload()

            # Start
            logger.info('Calling start method')
            self.client.loop.run_until_complete(tasker.start(self.client))

            # End
            logger.info('Calling end method')
            tasker.end()
        except TaskerError as e:
            logger.critical(e)
        except Exception as e:
            raise e
