========
BaseClients
========

BaseClient object
==========
The BaseClient object is the base class for all clients. It provides the basic functionality for all clients. 
It is not meant to be used directly. Instead, use one of the subclasses. 
BaseClient supports iteraction with node url and cleos.

.. autoclass:: litewax.baseclients.BaseClient
    :members:


AnchorClient object
==========
Class for iteracting with private, public keys, signing transactions. Based on `eospy.cleos <https://github.com/eosnewyork/eospy/blob/master/eospy/cleos.py#L16>`_.

.. autoclass:: litewax.baseclients.AnchorClient
    :members:


WCWClient object
==========
Class for iteracting with blockchain via Wax Cloud Wallet Client by cookies. Use Wax Cloud Wallet for sing transaction.
Provide token session for authorization.

.. autoclass:: litewax.baseclients.WCWClient
    :members: