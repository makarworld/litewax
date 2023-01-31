from __future__ import annotations
import typing
from eospy.types import Transaction as EosTransaction
from eospy.utils import sig_digest
import datetime as dt
import pytz

from .baseclients import AnchorClient, WCWClient
from .types import TransactionInfo, WAXPayer
from .payers import AtomicHub, NeftyBlocks
from .contract import Contract, Action, ExampleContract
from .exceptions import (
    CPUlimit, AuthNotFound,
    ExpiredTransaction, UnknownError
)

class Client:
    """
    Client for interacting with the blockchain

    :param private_key: Private key string (if cookie is not provided)
    :type private_key: str
    :param cookie: WCW session token (if private_key is not provided)
    :type cookie: str
    :param node: Node URL
    :type node: str

    :Example:

    >>> from litewax import Client
    >>> # init client with private key
    >>> client = Client(private_key=private_key)
    >>> # or init client with WCW session token
    >>> client = Client(cookie=cookie)
    >>> client.Transaction(
    >>>     client.Contract("eosio.token").transfer(
    >>>         "from", "to", "1.00000000 WAX", "memo"
    >>>     )
    >>> ).push()
    """
    __slots__ = ("root", "node", "wax", "name", "change_node", "sign")

    def __init__(self, private_key: typing.Optional[str] = "", cookie: typing.Optional[str] = "", node: typing.Optional[str] = "https://wax.greymass.com") -> None:
        if private_key:
            self.root = AnchorClient(private_key, node)

        elif cookie:
            self.root = WCWClient(cookie, node)
            
        else:
            raise ValueError("You must provide a private key or a WCW session token")

        # set methods
        self.__setattr__("change_node", self.root.change_node)
        self.__setattr__("sign", self.root.sign)

        # set variables
        self.__setattr__("node", self.root.node)
        self.__setattr__("wax", self.root.wax)
        self.__setattr__("name", self.root.name)

    def __str__(self):
        return f"Client(name={self.name}, node={self.node})"

    def Contract(self, name: str, actor: typing.Optional[typing.Union[str, None]] = None, force_recreate: typing.Optional[bool] = False, node: typing.Optional[str] = None) -> ExampleContract:
        """
        Create a :obj:`litewax.contract.ExampleContract` object

        :param name: contract name
        :type name: str
        :param actor: actor name
        :type actor: str
        :param force_recreate: force recreate contract object
        :type force_recreate: bool
        :param node: node url
        :type node: str

        :return: `litewax.contract.ExampleContract` object
        :rtype: litewax.contract.ExampleContract

        :Example:

        >>> from litewax import Client
        >>> # init client with private key
        >>> client = Client(private_key=private_key)
        >>> # create contract object
        >>> contract = client.Contract("eosio.token")
        >>> # create action object
        >>> action = contract.transfer("from", "to", "1.00000000 WAX", "memo")
        >>> # create transaction object
        >>> trx = client.Transaction(action)
        >>> # push transaction
        >>> trx.push()

        """
        return Contract(name, self, actor=actor, force_recreate=force_recreate, node=node)

    def Transaction(self, *actions: tuple[Action, ...]) -> Transaction:
        """
        Create a `litewax.Transaction` object

        :param actions: actions of contracts
        :type actions: tuple

        :return: :class:`litewax.clients.Transaction` object
        :rtype: litewax.clients.Transaction

        :Example:

        >>> from litewax import Client
        >>> # init client with private key
        >>> client = Client(private_key=private_key)
        >>> # create transaction object
        >>> trx = client.Transaction(
        >>>     client.Contract("eosio.token").transfer(
        >>>         "from", "to", "1.00000000 WAX", "memo"
        >>>     )
        >>> )
        >>> # push transaction
        >>> trx.push()
        """
        return Transaction(self, *actions)

class Transaction:
    """
    :class:`litewax.Transaction` object
    Create a transaction object for pushing to the blockchain

    :param client: :obj:`litewax.Client` object
    :type client: litewax.clients.Client
    :param actions: actions of contracts
    :type actions: tuple[Action, ...]

    :Example:

    >>> from litewax import Client
    >>> # init client with private key
    >>> client = Client(private_key=private_key)
    >>> # create transaction object
    >>> trx = client.Transaction(
    >>>     client.Contract("eosio.token").transfer(
    >>>         "account1", "account2", "1.00000000 WAX", "memo"
    >>>     )
    >>> )
    >>> print(trx)
    litewax.Client.Transaction(
        node=https://wax.greymass.com,
        sender=account1,
        actions=[
            [active] account1 > eosio.token::transfer({"from": "account1", "to": "account2", "quantity": "1.00000000 WAX", "memo": "memo"})
        ]
    )
    >>> # Add payer for CPU
    >>> # init payer client with private key
    >>> payer = Client(private_key=private_key2)
    >>> # add payer to transaction
    >>> trx = trx.payer(payer)
    >>> print(trx)
    litewax.MultiClient.MultiTransaction(
        node=ttps://wax.greymass.com,
        accounts=[account1, account2],
        actions=[
            [active] account1 > eosio.token::transfer({"from": "account1", "to": "account2", "quantity": "1.00000000 WAX", "memo": "memo"}),
            [active] account2 > litewaxpayer::noop({})
        ]
    )
    >>> # push transaction
    >>> push_resp = trx.push()
    >>> print(push_resp)
    {'transaction_id': '928802d253bffc29d6178e634052ec5f044b2fcce0c4c8bc5b44d978e22ec5d4', ...}
    ```
    """
    __slots__ = ("client", "actions")

    def __init__(self, client: Client, *actions: tuple[Action, ...]):
        self.client = client

        if not actions:
            raise ValueError("Transaction must have at least one action")

        self.actions = list(actions)
        self.actions.reverse()

    def __str__(self):
        actions = ',\n        '.join([str(x) for x in self.actions])
        return f"""litewax.Client.Transaction(
    node={self.client.node},
    sender={self.client.name},
    actions=[
        {actions}
    ]
)"""

    def payer(self, payer: typing.Union[Client, WAXPayer.ATOMICHUB, WAXPayer.NEFTYBLOCKS, str], permission: typing.Optional[str] = "active") -> typing.Union[MultiTransaction, AtomicHub, NeftyBlocks]:
        """
        Set payer for all actions

        :param payer: payer name or `litewax.Client` object
        :type payer: litewax.clients.Client or str
        :param permission: payer permission (optional): default `active`
        :type permission: str

        :raises: `NotImplementedError` if payer is not :ref:`litewax.clients.Client`, :ref:`litewax.payers.AtomicHub` or :ref:`litewax.payers.NeftyBlocks`.

        :return: :class:`litewax.clients.MultiTransaction` object or :class:`litewax.payers.AtomicHub` object or :class:`litewax.payers.NeftyBlocks` object
        :rtype: litewax.clients.MultiTransaction or litewax.payers.AtomicHub or litewax.payers.NeftyBlocks
        """
        self.client = MultiClient(clients=[self.client], node=self.client.node)

        if isinstance(payer, Client):
            # Client transform to MultiClient
            if payer.name != self.client[0].name:
                self.client.append(payer)

            self.actions.reverse()
            self.actions.append(
                Contract(
                    name       = "litewaxpayer", 
                    client     = payer, 
                    permission = permission,
                    node       = self.client[0].node
                ).noop()
            )

            return self.client.Transaction(*self.actions)

        elif payer.lower() == WAXPayer.ATOMICHUB:
            return AtomicHub(self.client, self)
        
        elif payer.lower() == WAXPayer.NEFTYBLOCKS:
            return NeftyBlocks(self.client, self)

        else:
            raise NotImplementedError("Only AtomicHub and NeftyBlocks are supported.")


    def prepare_trx(self, chain_info: typing.Optional[dict] = {}, lib_info: typing.Optional[dict] = {}, expiration: typing.Optional[int] = 180) -> TransactionInfo:
        """
        Sign transaction with client and return :obj:`litewax.types.TransactionInfo`.

        :param chain_info: chain info. Provide it if you not want to get it from blockchain (optional)
        :type chain_info: dict
        :param lib_info: lib info. Provide it if you not want to get it from blockchain (optional)
        :type lib_info: dict
        :param expiration: transaction expiration time in seconds (optional): default 180
        :type expiration: int

        :return: :obj:`litewax.types.TransactionInfo`
        :rtype: litewax.types.TransactionInfo
        """
        transaction = {
            "actions": [a.result for a in self.actions]
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds = expiration)).replace(tzinfo=pytz.UTC))

        # Provide it if you not want to get it from blockchain
        if not chain_info or not lib_info:
            chain_info, lib_info = self.client.wax.get_chain_lib_info()

        trx = EosTransaction(transaction, chain_info, lib_info)

        if isinstance(self.client.root, AnchorClient):
            digest = sig_digest(trx.encode(), chain_info['chain_id'])
            signatures = self.client.sign(digest)
        else:
            signatures = self.client.sign(trx.encode())

        return TransactionInfo(
            signatures = signatures, 
            packed     = trx.encode().hex(), 
            serealized = [x for x in trx.encode()]
        )

    def push(self, data: typing.Optional[TransactionInfo] = {}, expiration: typing.Optional[int] = 180) -> dict:
        """
        Push transaction to blockchain

        :param data: :obj:`litewax.types.TransactionInfo` object (optional)
        :type data: litewax.types.TransactionInfo
        :param expiration: transaction expiration time in seconds (optional): default 180
        :type expiration: int

        :raises: `litewax.exceptions.CPUlimit` if transaction exceeded the current CPU usage limit imposed on the transaction
        :raises: `litewax.exceptions.ExpiredTransaction` if transaction is expired
        :raises: `litewax.exceptions.UnknownError` if unknown error

        :return: transaction information
        :rtype: dict
        """
        if not data or not isinstance(data, TransactionInfo):
            data = self.prepare_trx(expiration = expiration)

        push_create_offer = self.client.wax.post(
            "chain.push_transaction",
            json={
                "signatures": data.signatures,
                "compression": 0,
                "packed_context_free_data": "",
                "packed_trx": data.packed
            },
            timeout=30
        )
        
        if push_create_offer['transaction_id'] == '':
            if push_create_offer['error']["what"] == 'Transaction exceeded the current CPU usage limit imposed on the transaction':
                raise CPUlimit('Error: CPU usage limit!!')

            elif push_create_offer['error']["what"] == 'Expired Transaction':
                raise ExpiredTransaction('Error: Expired Transaction!!')
            else:
                raise UnknownError(
                    f'Error: {push_create_offer["error"]["details"][0]["message"]}')

        return push_create_offer





class MultiClient:
    """
    Bases: :class:`list`

    MultiClient class for interacting with blockchain using many clients.

    :param private_keys: list of private keys (optional)
    :type private_keys: list
    :param cookies: list of cookies (optional)
    :type cookies: list
    :param clients: list of `litewax.clients.Client` objects (optional)
    :type clients: list
    :param node: node url (optional): default https://wax.greymass.com
    :type node: str

    :raises: `litewax.exceptions.AuthNotFound` if you not provide a private key, a cookie or a clients

    :Example:

    >>> from litewax import MultiClient
    >>> client = MultiClient(
    >>>     private_keys = [
    >>>         "EOS7...1",
    >>>         "EOS7...2",
    >>>         "EOS7...3"
    >>>     ],
    >>>     node = "https://wax.greymass.com"
    >>> )
    >>> # Change node
    >>> client.change_node("https://wax.eosn.io")
    >>> # Append client
    >>> client.append(Client(private_key="EOS7...4"))
    >>> # Create transaction
    >>> trx = client.Transaction(
    >>>     Contract("eosio.token").transfer(
    >>>         "account1", "account2", "1.0000 WAX", "memo"
    >>>     )
    >>> )
    >>> # Add payer
    >>> trx = trx.payer(client[2])
    >>> # Push transaction
    >>> trx.push()
    """
    __slots__ = ("clients")

    def __init__(self, 
            private_keys: typing.Optional[typing.List[str]] = [], 
            cookies: typing.Optional[typing.List[str]] = [],  
            clients: typing.Optional[typing.List[Client]] = [], 
            node: typing.Optional[str] = 'https://wax.greymass.com'):
        self.clients = clients
        if clients:
            self.change_node(node)

        if not cookies and not private_keys and not clients:
            raise AuthNotFound("You must provide a private key, a cookie or a clients")

        for private_key in private_keys:
            self.clients.append(Client(private_key=private_key, node=node))

        for cookie in cookies:
            self.clients.append(Client(cookie=cookie, node=node))

    def __str__(self) -> str:
        return f"MultiClient(clients={self.clients})"

    def change_node(self, node: str):
        """
        Change node url for all clients
        
        :param node: Node URL
        :type node: str
        
        :return:
        :rtype: None
        """
        for client in self.clients:
            client.change_node(node)

    def __getitem__(self, index):
        return self.clients[index]

    def __len__(self):
        return len(self.clients)
    
    def __iter__(self):
        return iter(self.clients)
    
    def __next__(self):
        return next(self.clients)
    
    def append(self, client: Client) -> None:
        """
        Append client to clients list
        
        :param client: `litewax.Client` object
        :type client: litewax.clients.Client

        :return:
        :rtype: None
        """
        self.clients.append(client)

    def sign(self, 
                trx: bytearray, 
                whitelist: typing.Optional[typing.List[str]] = [], 
                chain_id: typing.Optional[str] = None) -> typing.List[str]:
        """
        Sign a transaction with all whitelisted clients
        
        :param trx: bytearray of transaction
        :type trx: bytearray
        :param whitelist: list of clients to sign with (optional)
        :type whitelist: list
        :param chain_id: chain id of the network (optional)
        :type chain_id: str

        :return: list of signatures
        :rtype: list
        """
        if not chain_id:
            chain_id = self.clients[0].wax.get_info()['chain_id']

        digest = sig_digest(trx, chain_id)

        signatures = []

        for client in self.clients:
            if client.name not in whitelist: continue

            if isinstance(client.root, AnchorClient):
                signatures += client.sign(digest)
            else:
                signatures += client.sign(trx)

        return signatures

    def Transaction(self, *actions: tuple[Action, ...]):
        """
        Create a :obj:`litewax.MultiTransaction` object

        :arg actions: list of actions
        :type actions: tuple

        :return: :obj:`litewax.MultiTransaction` object
        :rtype: litewax.clients.MultiTransaction

        :Example:

        >>> from litewax import Client, MultiClient
        >>> # init client with private key
        >>> client1 = Client(private_key=private_key1)
        >>> client2 = Client(private_key=private_key2)
        >>> multi_client = MultiClient(clients=[client1, client2])
        >>> # create transaction object
        >>> trx = multi_client.Transaction(
        >>>     multi_client[1].Contract("eosio.token").transfer(
        >>>         "from", "to", "1.00000000 WAX", "memo"
        >>>     ),
        >>>     multi_client[0].Contract("litewaxpayer").noop()
        >>> )
        >>> # push transaction
        >>> trx.push()
        """
        return MultiTransaction(self, *actions)

class MultiTransaction:
    """
    MultiTransaction class for creating and pushing transactions using many signatures

    :param client: `litewax.MultiClient` object
    :type client: litewax.clients.MultiClient
    :param actions: list of actions
    :type actions: tuple

    :Example:

    >>> from litewax import MultiClient
    >>> # init client with private keys
    >>> client = MultiClient(
    >>>     private_keys = [
    >>>         "EOS7...1",
    >>>         "EOS7...2"
    >>>     ],
    >>>     node = "https://wax.greymass.com"
    >>> )
    >>> # create transaction object
    >>> trx = client.Transaction(
    >>>     client[0].Contract("eosio.token").transfer(
    >>>         "from", "to", "1.00000000 WAX", "memo"
    >>>     )
    >>> )
    >>> # add payer
    >>> trx = trx.payer(client[1])
    >>> # push transaction
    >>> trx.push()

    """
    __slots__ = ("client", "actions")

    def __init__(self, client: MultiClient, *actions: tuple[Action, ...]):
        self.client = client

        self.actions = list(actions)
        self.actions.reverse()

    def __str__(self) -> str:
        """return string representation of transaction"""
        actions = ',\n        '.join([str(x) for x in self.actions])
        return f"""litewax.MultiClient.MultiTransaction(
    node={self.client[0].node},
    accounts=[{', '.join([x.name for x in self.client])}],
    actions=[
        {actions}
    ]
)"""

    def payer(self, payer: typing.Union[Client, WAXPayer.ATOMICHUB, WAXPayer.NEFTYBLOCKS, str], permission: typing.Optional[str] = "active") -> typing.Union[MultiTransaction, AtomicHub, NeftyBlocks]:
        """
        Set payer

        :param payer: payer account name or `litewax.Client` object
        :type payer: str or litewax.clients.Client
        :param permission: payer permission (optional): default `active`
        :type permission: str

        :raise NotImplementedError: if payer is not :ref:`litewax.clients.Client`, :ref:`litewax.payers.AtomicHub` or :ref:`litewax.payers.NeftyBlocks`

        :return: `litewax.clients.MultiTransaction` object or `litewax.payers.AtomicHub` or `litewax.payers.NeftyBlocks` object
        :rtype: litewax.clients.MultiTransaction or litewax.payers.AtomicHub or litewax.payers.NeftyBlocks
        """
        if isinstance(payer, Client):
            if payer.name not in [x.name for x in self.client]:
                self.client.append(payer)

            # append payer action to first position
            self.actions = [
                Contract(
                    name       = "litewaxpayer", 
                    client     = payer, 
                    actor      = payer.name, 
                    permission = permission, 
                    node       = self.client[0].node
            ).noop()] + self.actions

            return self

        elif payer.lower() == WAXPayer.ATOMICHUB:
            return AtomicHub(self.client, self)
        
        elif payer.lower() == WAXPayer.NEFTYBLOCKS:
            return NeftyBlocks(self.client, self)

        else:
            raise NotImplementedError("Only AtomicHub and NeftyBlocks are supported.")


    def prepare_trx(self, chain_info: typing.Optional[dict] = {}, lib_info: typing.Optional[dict] = {}, expiration: typing.Optional[int] = 180) -> TransactionInfo:
        """
        Sign transaction with clients and return signatures, packed and serialized transaction

        :param chain_info: chain info. Provide it if you not want to get it from blockchain (optional)
        :type chain_info: dict
        :param lib_info: lib info. Provide it if you not want to get it from blockchain (optional)
        :type lib_info: dict
        :param expiration: transaction expiration time in seconds (optional): default 180
        :type expiration: int

        :return: :obj:`litewax.types.TransactionInfo` object
        :rtype: litewax.types.TransactionInfo
        """
        transaction = {
            "actions": [a.result for a in self.actions]
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=expiration)).replace(tzinfo=pytz.UTC))
        
        if not chain_info or not lib_info:
            chain_info, lib_info = self.client[0].wax.get_chain_lib_info()
        trx = EosTransaction(transaction, chain_info, lib_info)

        whitelist = [action.result['authorization'][0]['actor'] for action in self.actions]

        signatures = self.client.sign(trx.encode(), whitelist, chain_info['chain_id'])

        return TransactionInfo(
            signatures = signatures, 
            packed = trx.encode().hex(), 
            serealized = [x for x in trx.encode()]
        )

    def push(self, data: typing.Optional[TransactionInfo] = {}, expiration: typing.Optional[int] = 180) -> dict:
        """
        Push transaction to blockchain

        :param data: :obj:`litewax.types.TransactionInfo` object (optional)
        :type data: litewax.types.TransactionInfo
        :param expiration: transaction expiration time in seconds (optional): default 180
        :type expiration: int

        :raises: `litewax.exceptions.CPUlimit` if transaction exceeded the current CPU usage limit imposed on the transaction
        :raises: `litewax.exceptions.ExpiredTransaction` if transaction is expired
        :raises: `litewax.exceptions.UnknownError` if unknown error

        :return: transaction information
        :rtype: dict
        """
        if not data or not isinstance(data, TransactionInfo):
            data = self.prepare_trx(expiration = expiration)

        push_create_offer = self.client[0].wax.post(
            "chain.push_transaction",
            json={
                "signatures": data.signatures,
                "compression": 0,
                "packed_context_free_data": "",
                "packed_trx": data.packed
            },
            timeout=30
        )
        
        if push_create_offer['transaction_id'] == '':
            if push_create_offer['error']["what"] == 'Transaction exceeded the current CPU usage limit imposed on the transaction':
                raise CPUlimit('Error: CPU usage limit!!')

            elif push_create_offer['error']["what"] == 'Expired Transaction':
                raise ExpiredTransaction('Error: Expired Transaction!!')
            else:
                raise UnknownError(
                    f'Error: {push_create_offer["error"]["details"][0]["message"]}')

        return push_create_offer
