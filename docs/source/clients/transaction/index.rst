========
Transaction object
========

.. _litewax.clients.Transaction:
.. _litewax.Transaction:

Transaction
-------------
Used by `litewax.clients.Client` class. 

This transaction may be signed with only one client.

May transform to `litewax.clients.MultiTransaction` object if you use :meth:`litewax.clients.Transaction.payer` method with `litewax.clients.Client` as payer.

.. autoclass:: litewax.clients.Transaction
    :members:
    :undoc-members:


.. _litewax.clients.MultiTransaction:
.. _litewax.MultiTransaction:

MultiTransaction
-------------
Used by `litewax.clients.Client` class. 

This transaction may be signed with many clients.


.. autoclass:: litewax.clients.MultiTransaction
    :members:
    :undoc-members: