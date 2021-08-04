Telegram Tasks Processor
========================

A.K.A **t2p**.

Tool to execute tasks through Telegram userbot.


Quickstart
----------

1. Install the Python package:

.. code-block:: bash

    # via pip:
    pip install .

    # or via setup script:
    python setup.py install

2. Have a Telegram account. You can create it if you do not have, see the `Telegram official website <https://telegram.org/>`_.
3. Create a Telegram Application. This `official post <https://core.telegram.org/api/obtaining_api_id>`_ says how to create it.
4. Once the Telegram Application is created, you must copy *config.ini.sample* to *config.ini* and edit it. The most important are the fields *id* (the *api_id* provided) and *hash* (the *api_hash* provided).
5. Open a terminal and run:

.. code-block:: bash

 t2p
 # or type this for help
 t2p --help
