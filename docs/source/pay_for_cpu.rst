.. _cpu-payers:

Different ways to set a payer for CPU
=====================================

Simple template
---------------

All transactions in EOS-based blockchains use the CPU to process transaction by node.
See `CPU bandwidth <https://developers.eos.io/welcome/latest/glossary/index/#cpu>`_ for understanding how CPU works.

.. seealso:: 
    
    * `How to set a payer <https://developers.eos.io/manuals/eosjs/latest/how-to-guides/how-to-set-a-payer>`_
    
    * `CPU bandwidth <https://developers.eos.io/welcome/latest/glossary/index/#cpu>`_ 
    
    * `Delegate CPU <https://developers.eos.io/manuals/eos/v2.0/cleos/how-to-guides/how-to-delegate-CPU-resource>`_
    
    * `Undelegate CPU <https://developers.eos.io/manuals/eos/v2.0/cleos/how-to-guides/how-to-undelegate-CPU>`_


In :ref:`litewax` you can set the payer of the CPU for a transaction. 
Before, import and initialize 2 clients, one for the payer and one for the sender.

.. code-block:: python

    from litewax import Client, WAXPayer

    # create sender Client instance
    sender = Client(private_key='5K1...') 

    # create payer Client instance
    payer = Client(private_key='5K2...') 

Next: Create a :ref:`litewax.Transaction`.

.. code-block:: python

    # create transaction
    trx = sender.Transaction(
        sender.Contract('eosio.token').transfer(
            _from=sender.name, 
            to='receiver', 
            quantity='1.00000000 WAX', 
            memo='memo'
        )
    )

Now, set the payer of the CPU for the :ref:`litewax.Transaction`.
Payer can be set in different ways:

* by other :ref:`litewax.Client`.

.. code-block:: python

    trx = trx.payer(payer)

* by :ref:`litewax.payers.AtomicHub`. If you don't have enough CPU, and actions in whitelist by atomichub like: atomicassets.transfer(). (Only WAX mainnet)

.. code-block:: python

    trx = trx.payer(WAXPayer.ATOMICHUB)

* by :ref:`litewax.payers.NeftyBlocks`. If actions in whitelist by neftyblocks like: neftyblocksd.claim_drop(). (Only WAX mainnet and testnet)

.. code-block:: python

    trx = trx.payer(WAXPayer.NEFTYBLOCKS)

* or if you use a :ref:`litewax.MultiClient`, you can set the payer when creating a :ref:`litewax.MultiTransaction`.

.. code-block:: python

    from litewax import MultiClient

    # create MultiClient instance
    client = MultiClient(private_keys=['5K1...', '5K2...', '5K3...'])

    # create transaction.
    # 1st client send 1 WAX to 2nd client, 
    # 2nd client send 1 WAX to 1st client, 
    # 3rd client pay CPU.
    trx = sender.Transaction(
        # some 1st action
        client[0].Contract('eosio.token').transfer(
            _from=client[0].name, 
            to=client[1].name, 
            quantity='1.00000000 WAX', 
            memo='memo'
        ),

        # some 2nd action
        client[1].Contract('eosio.token').transfer(
            _from=client[1].name, 
            to=client[0].name, 
            quantity='1.00000000 WAX', 
            memo='memo'
        ),

        # add last action for pay CPU. You can use any contract and action. litewax owner created a custom empty contract, which has only one .noop() action in mainnet and testnet.
        client[2].Contract('litewaxpayer').noop()
    )

Last step: Push transaction.

.. code-block:: python

    # send transaction
    trx.push()

.. note::
    If you set the payer of the CPU for the transaction, you must have enough CPU for the payer. 
    If you don't have enough CPU, you can delegate CPU to the payer.

    See `Delegate CPU <https://developers.eos.io/manuals/eos/v2.0/cleos/how-to-guides/how-to-delegate-CPU-resource>`_ for more information.

.. seealso::

    `Contract usage examples <https://litewax.readthedocs.io/en/latest/contract_usage_examples.html>`_

Summary
-------

.. code-block:: python

    from litewax import Client, MultiClient, WAXPayer

    # 1. create sender and payer Client instances
    sender = Client(private_key='5K1...') 
    payer = Client(private_key='5K2...') 

    # or create MultiClient instance
    # client = MultiClient(private_keys=['5K1...', '5K2...', '5K3...'])

    # 2. create transaction with sender
    trx = sender.Transaction(
        sender.Contract('eosio.token').transfer(
            _from=sender.name, 
            to='receiver', 
            quantity='1.00000000 WAX', 
            memo='memo'
        )
    )

    # or create payed transaction with MultiClient
    # create transaction.
    # 1st client send 1 WAX to 2nd client, 
    # 2nd client send 1 WAX to 1st client, 
    # 3rd client pay CPU.
    #
    # trx = sender.Transaction(
    #     # some 1st action
    #     client[0].Contract('eosio.token').transfer(
    #         _from=client[0].name, 
    #         to=client[1].name, 
    #         quantity='1.00000000 WAX', 
    #         memo='memo'
    #     ),
    #
    #     # some 2nd action
    #     client[1].Contract('eosio.token').transfer(
    #         _from=client[1].name, 
    #         to=client[0].name, 
    #         quantity='1.00000000 WAX', 
    #         memo='memo'
    #     ),
    #
    #     # add last action for pay CPU. You can use any contract and action. litewax owner created a custom empty contract, which has only one .noop() action in mainnet and testnet.
    #     client[2].Contract('litewaxpayer').noop()
    # )

    # 3. set payer of the CPU for the transaction
    trx = trx.payer(payer)

    # or set atomichub as a payer
    # trx = trx.payer(WAXPayer.ATOMICHUB)

    # or set neftyblocks as a payer
    # trx = trx.payer(WAXPayer.NEFTYBLOCKS)

    # 4. send transaction
    resp = trx.push()
    print(resp)
    # {"transaction_id": "b0e...", ...}


