from typing import List, Any
import eospy.keys
import eospy.dynamic_url
from eospy.types import Transaction as EosTransaction
from eospy.utils import sig_digest
import datetime as dt
import pytz

from .baseclients import AnchorClient, WCWClient
from .types import TransactionInfo, WAXPayer
from .payers import AtomicHub, NeftyBlocks
from .contract import Contract
from .exceptions import (
    CPUlimit, AuthNotFound,
    ExpiredTransaction, UnknownError
)

class Client:
    """
    ## Client for interacting with the blockchain

    ### Methods:
        - __init__( private_key: str, cookie: str, node: str )
        - sign( trx: bytearray )
        - change_node( node: str )

    ### Variables:
        - node (str): node url
        - wax (Cleos): eospy.cleos.Cleos object
        - name (str): wallet name
    
    ---

    ## Examples:
    ```python

    from litewax import Client

    # init client with private key
    client = Client(private_key=private_key)

    # or init client with WCW session token
    client = Client(cookie=cookie)

    client.Transaction(
        client.Contract("eosio.token").transfer(
            "from", "to", "1.00000000 WAX", "memo"
        )
    ).push()

    ```
    
    """
    __slots__ = ("node", "wax", "name", "client")

    def __init__(self, private_key: str = "", cookie: str = "", node: str = "https://wax.greymass.com") -> None:
        """Init a client for interacting with the blockchain"""
        if private_key:
            self.root = AnchorClient(private_key, node)

        elif cookie:
            self.root = WCWClient(cookie, node)

        # set methods
        self.__setattr__("change_node", self.root.change_node)
        self.__setattr__("sign", self.root.sign)

        # set variables
        self.__setattr__("node", self.root.node)
        self.__setattr__("wax", self.root.wax)
        self.__setattr__("name", self.root.name)

    def __str__(self):
        return f"Client(name={self.name}, node={self.node})"

    def Contract(self, name: str, actor: str=None, force_recreate: bool=False, node: str=None):
        """
        ## Create a `litewax.Contract` object

        ### Args:
            - name (str): contract name
            - actor (str): actor name
            - force_recreate (bool): force recreate contract object
            - node (str): node url

        ### Returns:
            - Contract: `litewax.Contract` object
        
        ---

        ## Examples:
        ```python
        from litewax import Client

        # init client with private key
        client = Client(private_key=private_key)

        # create contract object
        contract = client.Contract("eosio.token")

        # create action object
        action = contract.transfer("from", "to", "1.00000000 WAX", "memo")

        # create transaction object
        trx = client.Transaction(action)

        # push transaction
        trx.push()

        """
        return Contract(name, self, actor=actor, force_recreate=force_recreate, node=node)

    def Transaction(self, *actions):
        """
        ## Create a `litewax.Client.Transaction` object

        ### Args:
            - actions (list): list of actions

        ### Returns:
            - Transaction: `litewax.Client.Transaction` object

        ---

        ## Examples:

        ```python
        from litewax import Client

        # init client with private key
        client = Client(private_key=private_key)

        # create transaction object
        trx = client.Transaction(
            client.Contract("eosio.token").transfer(
                "from", "to", "1.00000000 WAX", "memo"
            )
        )

        # push transaction
        trx.push()

        ```
        
        """
        return Transaction(self, *actions)

class Transaction:
    """
    ### Methods:
    - pay_with
    - get_trx_extend_info
    - push
    """
    def __init__(self, client: Client, *actions):
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

    def payer(self, payer: Any[WAXPayer, Client, str], permission: str = "active"):
        """
        ## Set payer for all actions

        ### Args:
            - payer (str | Client): payer name or `litewax.Client` object

        ### Returns:
            - Transaction: `litewax.Client.Transaction` object
        """
        self.client = MultiClient(clients=[self.client], node=self.client.node)

        if isinstance(payer, Client):
            # Client transform to MultiClient
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


    def prepare_trx(self) -> TransactionInfo:
        """
        ## Sign transaction with client

        Sign transaction with client and return signatures, packed and serialized transaction

        ### Returns:
            - TransactionInfo: `litewax.Client.TransactionInfo` object
        """
        transaction = {
            "actions": [a.result for a in self.actions]
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

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

    def push(self) -> dict:
        """
        ## Push transaction
        Push transaction to blockchain

        ### Returns:
        - dict: transaction info
        """
        data = self.prepare_trx()

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
    __slots__ = ("clients")

    def __init__(self, 
            private_keys: list = [], 
            cookies: list = [],  
            clients: List[Client] = [], 
            node: str='https://wax.greymass.com'):

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
    
    def append(self, client: Client):
        self.clients.append(client)

    def sign(self, 
                trx: bytearray, 
                whitelist: List[str] = [], 
                chain_id: str = "") -> list:
        """
        ## Sign a transaction with all clients
        
        ### Args:
        - trx (bytearray): bytearray of transaction
        - chain_id (str): chain id of the network (optional)

        ### Returns:
        - signatures (list): list of signatures
        """
        if not chain_id:
            chain_id = self.clients[0].wax.get_info()['chain_id']

        digest = sig_digest(trx, chain_id)

        signatures = []

        for client in self.clients:
            if client.name not in whitelist: continue

            if isinstance(client.root, AnchorClient):
                signatures += self.client.sign(digest)
            else:
                signatures += self.client.sign(trx)

        return signatures

    def Transaction(self, *actions):
        """
        ## Create a `litewax.MultiClient.Transaction` object

        ### Args:
            - actions (list): list of actions

        ### Returns:
            - Transaction: `litewax.MultiClient.Transaction` object

        ---

        ## Examples:

        ```python
        from litewax import Client, MultiClient

        # init client with private key
        client1 = Client(private_key=private_key1)
        client2 = Client(private_key=private_key2)

        multi_client = MultiClient(clients=[client1, client2])

        # create transaction object
        trx = multi_client.Transaction(
            multi_client[1].Contract("eosio.token").transfer(
                "from", "to", "1.00000000 WAX", "memo"
            ),
            multi_client[0].Contract("litewaxpayer").noop()
        )

        # push transaction
        trx.push()

        ```
        
        """
        return MultiTransaction(self, *actions)

class MultiTransaction:
    __slots__ = ("client", "actions")

    def __init__(self, client: MultiClient, *actions):
        self.client = client

        self.actions = list(actions)
        self.actions.reverse()

    def __str__(self):
        actions = ',\n        '.join([str(x) for x in self.actions])
        return f"""litewax.MultiClient.MultiTransaction(
    node={self.client[0].node},
    accounts=[{', '.join([x.name for x in self.client])}],
    actions=[
        {actions}
    ]
)"""

    def payer(self, payer: Any[Client, WAXPayer.ATOMICHUB, WAXPayer.NEFTYBLOCKS], permission: str = "active"):
        """
        ## Set payer

        ### Args:
            - payer (str): payer account name

        ### Returns:
            - Transaction: `litewax.MultiClient.MultiTransaction` object
        """
        if isinstance(payer, Client):
            self.client.append(payer)
            self.actions.append(
                Contract(
                    name       = "litewaxpayer", 
                    client     = payer, 
                    actor      = payer.name, 
                    permission = permission, 
                    node       = self.client[0].node
            ).noop())

            return self

        elif payer.lower() == WAXPayer.ATOMICHUB:
            return AtomicHub(self.client, self)
        
        elif payer.lower() == WAXPayer.NEFTYBLOCKS:
            return NeftyBlocks(self.client, self)

        else:
            raise NotImplementedError("Only AtomicHub and NeftyBlocks are supported.")


    def prepare_trx(self) -> TransactionInfo:
        transaction = {
            "actions": [a.result for a in self.actions]
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        chain_info, lib_info = self.client[0].wax.get_chain_lib_info()
        trx = EosTransaction(transaction, chain_info, lib_info)

        whitelist = [action.result['authorization'][0]['actor'] for action in self.actions]

        signatures = client.sign(trx, whitelist, chain_info['chain_id'])

        return TransactionInfo(
            signatures = signatures, 
            packed = trx.encode().hex(), 
            serealized = [x for x in trx.encode()]
        )

    def push(self) -> dict:
        """
        ## Push transaction
        Push transaction to blockchain

        ### Returns:
        - dict: transaction info
        """
        data = self.prepare_trx()

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

if __name__ == "__main__":
    client = MultiClient(
        private_keys=["5JJYyiPpopRaQs1o7wQE6X7X1V5mc1pcE6iXGLKCQ8YpdVfv7hL"],
        #cookies=["hY0u8DUYNXjucimdWDajkuX9cLGjNlNjukaV60JZ"]
    )
    print(client[0].__dict__)
    trx = client.Transaction(
        Contract("res.pink", client[0]).noop(),

    )
    print(trx.push())