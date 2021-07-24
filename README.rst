Telegram Tasks Processor
========================

A.K.A **t2p**.

Tool to execute tasks through Telegram userbot.


Quickstart
----------

#. Install via pip.

.. code-block:: bash

 pip install .

#. Have a Telegram account. You can create it if you do not have, see the `Telegram official website <https://telegram.org/>`_.
#. Create a Telegram Application. This `official post <https://core.telegram.org/api/obtaining_api_id>`_ says how to create it.
#. Once the Telegram Application is created, you must copy *config.ini.sample* to *config.ini* and edit it. The most important are the fields *id* (the *api_id* provided) and *hash* (the *api_hash* provided).
#. Open a terminal and run:

.. code-block:: bash

 t2p
 # or type this for help
 t2p --help
