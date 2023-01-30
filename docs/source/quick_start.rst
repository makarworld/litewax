===========
Quick start
===========

Simple template
---------------

At first you have to import Client from litewax

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :lines: 1

Then you have to initialize Client with private key or session_token from Wax Cloud Wallet.

.. note:: 
    
    :ref:`how-to-get-session-token`


Initialize Client with private key:

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :lines: 3-4

Initialize Client with session_token:

.. literalinclude:: ../../examples/transfer_tokens_wcw.py
    :language: python
    :lines: 3-4

Next step: Create you first transaction. For example, transfer tokens.

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :lines: 6-20

Last step: Push transaction to the blockchain.

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :lines: 22-25


.. seealso:: 

    :ref:`cpu-payers`


Summary
-------

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :linenos:
    :lines: 1-25