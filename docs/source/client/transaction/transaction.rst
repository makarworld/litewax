Transaction object
==========

Transaction
-------------
Transaction object based on :class:`litewax.clients.Transaction` class.
Used by :class:`litewax.clients.Client` class. 
May transform to :class:`litewax.clients.MultiTransaction` object if you use :method:`litewax.clients.Transaction.payer` method with :class:`litewax.clients.Client` as payer.

.. autoclass:: litewax.clients.Transaction
    :members:
    :show-inheritance: