import json
import time
import eospy.cleos
import eospy.keys
from eospy.types import EOSEncoder, Transaction
from eospy.utils import sig_digest

import pytz
import datetime as dt
from anchor import Anchor


from client import Client

from contract import Contract
from exceptions import *
from wcw import WCW, TxConverter

class MultiSigClient():
    """
    ### IN WORKIND
    ## MultiSigClient
    With this class you can write transactions with many signs.
    This class works with list of private keys or list of cookies.
    WCW and Achor cannot be mixed. :(

    ### Example
    ```python
    from waxlite import MultiSigClient, Contract

    client = MultiSigClient(private_keys=["1", "2"])

    # Last signed action will pay for all CPU
    trx = client.Transaction(
        Contract("eosio.token", client[0]).transfer(
            _from = client[0].name,
            _to = client[1].name,
            amount = "1.0000 WAX",
            memo = "Send 1 WAX with MultiSigClient"
        ),
        Contract("res.pink", client[1]).noop() # for pay transaction
    )
    
    trx.push() # -> hash

    ```
    """
    def __init__(self, 
            private_keys: list=[], 
            cookies: list=[],  
            *clients: Client,
            node: str='https://wax.greymass.com'):

        self.anchor = False
        self.wcw = False

        self.clients = []
        self.anchors = []
        self.wcws = []

        if not cookies and not private_keys and not clients:
            raise AuthNotFound("You must providea private key, a cookie or a clients")

        if cookies and private_keys:
            raise NotImplementedError("You can't use both private keys and cookies :(")

        if private_keys:
            for private_key in private_keys:
                self.anchors.append(Anchor(private_key=private_key, node=node))
                self.anchor = True

        elif cookies:
            for cookie in cookies:
                self.wcws.append(WCW(session_token=cookie, node=node))
                self.wcw = True
        
        self.clients += self.anchors + self.wcws

        self.node = node

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
    def __init__(self, client: MultiSigClient, *actions, node: str='https://wax.greymass.com'):
        self.actions = actions
        self.client = client
        self.node = node
        self.wax = eospy.cleos.Cleos(url=node, version='v1')

    def push(self):
        
        trx_wallets = []
        for action in list(self.actions):
            trx_wallets.append(action['authorization'][0]['actor'])

        if self.client.anchor:
            # anchor part
            transaction = {
                "actions": list(self.actions)
            }
                
            transaction['expiration'] = str(
                (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

            chain_info, lib_info = self.wax.get_chain_lib_info()
            trx = Transaction(transaction, chain_info, lib_info)
            digest_anchor = sig_digest(trx.encode(), chain_info['chain_id'])
        
        if self.client.wcw:
            # wcw part
            block_data = self.client.wcws[0].utils.getBlock()

            diggest_wcw = TxConverter({
                "expiration": int(time.time() + 60),
                "ref_block_num": block_data['ref_block_num'],
                "ref_block_prefix": block_data['ref_block_prefix'],
                "max_net_usage_words": 0,
                "max_cpu_usage_ms": 0,
                "delay_sec": 0,
                "context_free_actions": [],
                "actions": list(self.actions),
                "transaction_extensions":[]
            }).bytes_list

        signatures = []

        for cl in self.client:
            if cl.name not in trx_wallets:
                continue

            if isinstance(cl, Anchor):
                signatures.append(cl.sign(digest_anchor))

            if isinstance(cl, WCW):
                signatures += cl.sign(diggest_wcw)


        if self.client.wcw:
            push_create_offer = self.client.wcws[0].utils.pushTx(signatures, diggest_wcw)
            if push_create_offer['transaction_id'] == '':
                if push_create_offer['error']["what"] == 'Transaction exceeded the current CPU usage limit imposed on the transaction':
                    raise CPUlimit('Error: CPU usage limit!!')
                elif push_create_offer['error']["what"] == 'Expired Transaction':
                    raise ExpiredTransaction('Error: Expired Transaction!!')
                else:
                    raise UnknownError(
                        f'Error: {push_create_offer["error"]["details"][0]["message"]}')
            return push_create_offer["transaction_id"]

        elif self.client.anchor:
            final_trx = {
                'compression': 0,
                'transaction': trx.__dict__,
                'signatures': signatures
            }

            data = json.dumps(final_trx, cls=EOSEncoder)

            return self.wax.post('chain.push_transaction', params=None, data=data, timeout=30)

if __name__ == "__main__":
    client = MultiSigClient(
        #private_keys=["5JJYyiPpopRaQs1o7wQE6X7X1V5mc1pcE6iXGLKCQ8YpdVfv7hL"],
        cookies=["hY0u8DUYNXjucimdWDajkuX9cLGjNlNjukaV60JZ"]
    )
    print(client[0].__dict__)
    trx = client.Transaction(
        Contract("res.pink", client[0]).noop(),
        #Contract("res.pink", client[1]).noop(),
        #Contract("res.pink", client[2]).noop()
    )
    print(trx.push())