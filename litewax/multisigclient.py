from typing import List
from eospy.types import Transaction
from eospy.utils import sig_digest
import eospy.cleos
import eospy.dynamic_url
import pytz
import datetime as dt

from .types import TransactionInfo
from .client import Client, AnchorClient
from .contract import Contract
from .exceptions import *
from .paywith import PayWith


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

    def sign(self, 
                trx: bytearray, 
                whitelist: List[str] = [], 
                chain_id: str = "") -> Transaction:
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
        return Transaction(self, *actions)

class Transaction:
    __slots__ = ("client", "actions")

    def __init__(self, client: MultiClient, *actions):
        self.client = client

        self.actions = list(actions)
        self.actions.reverse()

    def __str__(self):
        actions = ',\n        '.join([str(x) for x in self.actions])
        return f"""litewax.MultiSigClient.Transaction(
    node={self.client[0].node},
    accounts=[{', '.join([x.name for x in self.client])}],
    actions=[
        {actions}
    ]
)"""

    def prepare_trx(self):
        transaction = {
            "actions": [a.result for a in self.actions]
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        chain_info, lib_info = self.wax.get_chain_lib_info()
        trx = Transaction(transaction, chain_info, lib_info)

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