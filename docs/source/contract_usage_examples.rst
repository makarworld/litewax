.. _contract_usage_examples:

=======================
Contract usage examples
=======================

All transaction in EOS-based blockchain are executed by smart contracts.
:ref:`litewax` have :ref:`litewax.abigen` for generate .py files from contract abi which will got from node.


For example, we can generate `eosio_token.py` contract:

.. code-block:: bash

    $ python -c "from litewax import Contract; Contract('eosio.token')"

Then we can use `eosio_token.py` to call `eosio.token` contract:

.. code-block:: python

    from contracts.eosio_token import eosio_token
    contract = eosio_token(actor='alice', permission='active')
    single_action = contract.transfer('alice', 'bob', '1.00000000 WAX', 'memo')

You also can send transaction without any litewax :ref:`litewax.Client`. Only with generated contract file:

.. code-block:: python

    from contracts.eosio_token import eosio_token
    contract = eosio_token(actor='alice', permission='active')
    contract.push_actions(
        private_keys=['5K...'],
        contract.transfer('alice', 'bob', '1.00000000 WAX', 'memo')
    )

=======================

For easy iteracting with any contract, litewax have :ref:`litewax.Contract` function, 
which create a .py contract file, dynamicly import it and return initialized contract object:

.. code-block:: python

    from litewax import Contract
    contract = Contract('eosio.token', actor='alice')
    single_action = contract.transfer('alice', 'bob', '1.00000000 WAX', 'memo')

Also you can use :ref:`litewax.Contract` function in :ref:`litewax.clients.Client` object:

.. note:: 

    If you use :ref:`litewax.Contract` function in :ref:`litewax.clients.Client` object, 
    you don't need to specify `actor` in contract constructor, but may specify `permission` if need.


.. code-block:: python

    from litewax import Client
    client = Client(private_key='5K...', 'https://wax.greymass.com')
    contract = client.Contract('eosio.token')
    single_action = contract.transfer('alice', 'bob', '1.00000000 WAX', 'memo')

=======================