.. _quick-start:

===========
Quick start
===========

Simple template
---------------

At first you have to import :ref:`litewax.Client` from litewax

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :lines: 1

Then you have to initialize :ref:`litewax.Client` with private key or session_token from Wax Cloud Wallet.

.. note:: 
    
    :ref:`how-to-get-session-token`


Initialize :ref:`litewax.Client` with private key:

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :lines: 3-4

Initialize :ref:`litewax.Client` with session_token:

.. literalinclude:: ../../examples/transfer_tokens_wcw.py
    :language: python
    :lines: 3-4

Next step: Create you first :ref:`litewax.Transaction`. For example, transfer tokens.

.. literalinclude:: ../../examples/transfer_tokens.py
    :language: python
    :lines: 6-20

Last step: Push :ref:`litewax.Transaction` to the blockchain.

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