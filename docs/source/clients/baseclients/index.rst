========
BaseClients
========

.. _litewax.baseclients.BaseClient:

BaseClient object
==========
The BaseClient object is the base class for all clients. It provides the basic functionality for all clients. 
It is not meant to be used directly. Instead, use one of the subclasses. 
BaseClient supports iteraction with node url and cleos.

.. autoclass:: litewax.baseclients.BaseClient
    :members:
    :undoc-members:
    :private-members:

.. _litewax.baseclients.AnchorClient:

AnchorClient object
==========
Class for iteracting with private, public keys, signing transactions. Based on `eospy.cleos <https://github.com/eosnewyork/eospy/blob/master/eospy/cleos.py#L16>`_.

.. autoclass:: litewax.baseclients.AnchorClient
    :members:
    :undoc-members:

.. _litewax.baseclients.WCWClient:

WCWClient object
==========
Class for iteracting with blockchain via Wax Cloud Wallet Client by cookies. Use Wax Cloud Wallet for sing transaction.
Provide token session for authorization.

.. note:: 
    
    :ref:`how-to-get-session-token`


.. autoclass:: litewax.baseclients.WCWClient
    :members:
    :undoc-members: