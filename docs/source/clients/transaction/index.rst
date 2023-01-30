========
Transaction object
========

Transaction
-------------
Transaction object based on :class:`litewax.clients.Transaction` class.
Used by :class:`litewax.clients.Client` class. 
This transaction may be signed with only one client.
May transform to :class:`litewax.clients.MultiTransaction` object if you use :method:`litewax.clients.Transaction.payer` method with :class:`litewax.clients.Client` as payer.

.. autoclass:: litewax.clients.Transaction
    :members:
    :show-inheritance:


MultiTransaction
-------------
:class:`litewax.clients.MultiTransaction` object.
This transaction may be signed with many clients.
Used by :class:`litewax.clients.MultiClient` class. 

.. autoclass:: litewax.clients.MultiTransaction
    :members:
    :show-inheritance: