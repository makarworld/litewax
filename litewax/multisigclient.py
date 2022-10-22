from eospy.types import Transaction
from eospy.utils import sig_digest
import pytz
import datetime as dt

from .client import Client
from .contract import Contract
from .exceptions import *
from .paywith import PayWith


class MultiSigClient():
    """
    ### Methods:
    - SetNode
    - Transaction
    - Contract
    """
    def __init__(self, 
            private_keys: list=[], 
            cookies: list=[],  
            *clients: Client,
            node: str='https://wax.greymass.com'):

        self.node = node

        if not cookies and not private_keys and not clients:
            raise AuthNotFound("You must provide a private key, a cookie or a clients")

        self.clients = list(clients)

        for private_key in private_keys:
            self.clients.append(Client(private_key=private_key, node=node))

        for cookie in cookies:
            self.clients.append(Client(cookie=cookie, node=node))

        self.Contract = Contract

    def SetNode(self, node: str):
        self.node = node
        for client in self.clients:
            client.SetNode(node)

    def Transaction(self, *actions):
        return TX(self, *actions, node=self.node)

    def __getitem__(self, index):
        return self.clients[index]

    def __len__(self):
        return len(self.clients)
    
    def __iter__(self):
        return iter(self.clients)
    
    def __next__(self):
        return next(self.clients)

class TX():
    """
    ### Methods:
    - pay_with
    - get_trx_extend_info
    - push
    """
    def __init__(self, client: MultiSigClient, *actions, node: str='https://wax.greymass.com'):
        self.client = client
        self.node = node
        self.wax = self.client[0].wax

        self.actions = list(actions)

    def pay_with(self, payer: str, network='mainnet'):
        return PayWith(self, payer, network)

    def get_trx_extend_info(self):
        trx_wallets = []
        for action in list(self.actions):
            trx_wallets.append(action['authorization'][0]['actor'])

        transaction = {
            "actions": self.actions
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        chain_info, lib_info = self.wax.get_chain_lib_info()
        trx = Transaction(transaction, chain_info, lib_info)

        digest_anchor = sig_digest(trx.encode(), chain_info['chain_id'])

        signatures = []

        for cl in self.client:
            if cl.name not in trx_wallets:
                continue

            if cl.type == 'private_key':
                signatures.append(cl.sign(digest_anchor))

            if cl.type == 'cookie':
                signatures += cl.sign(trx.encode())

        return {
            "signatures": signatures,
            "packed": trx.encode().hex(),
            "serealized": [x for x in trx.encode()]
        }

    def push(self):
        info = self.get_trx_extend_info()
        signatures = info['signatures']
        packed = info['packed']

        push_create_offer = self.wax.post("chain.push_transaction",
            json={
                "signatures": signatures,
                "compression": 0,
                "packed_context_free_data": "",
                "packed_trx": packed
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
    client = MultiSigClient(
        private_keys=["5JJYyiPpopRaQs1o7wQE6X7X1V5mc1pcE6iXGLKCQ8YpdVfv7hL"],
        #cookies=["hY0u8DUYNXjucimdWDajkuX9cLGjNlNjukaV60JZ"]
    )
    print(client[0].__dict__)
    trx = client.Transaction(
        Contract("res.pink", client[0]).noop(),

    )
    print(trx.push())