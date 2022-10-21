"""
interface:
class Anchor:
    method GetName -> walletname
    method Transaction -> TX

class TX:
    method push -> hash
"""
import json
import time
from typing import Tuple

import eospy.cleos
import eospy.keys
from eospy.types import Transaction, EOSEncoder
from eospy.utils import sig_digest
from eospy.exceptions import EOSKeyError
from eospy.signer import Signer

import cloudscraper
import pytz
import datetime as dt

from .paywith import PayWith
from .contract import Contract

class Anchor:
    """
        ## Create Anchor wallet object\n
        ### Example:\n
        ```python
        from litewax import Client, Contract
        client = Client(private_key="")
        client.name # -> wallet name

        contract = Contract(name="eosio.token")
        contract.set_actor(client.name)

        trx = client.Transaction(
            contract.transfer(
                _from = "wallet1",
                _to = "wallet2",
                amount = "1.0000 WAX",
                memo = "memo"
            )
        )

        trx.push() # -> hash
        ```
        
        - Returns
          - `TX` Object
    """

    def __init__(self, private_key, node="https://wax.greymass.com"):
        self.private_key = private_key
        self.public_key = eospy.keys.EOSKey(private_key).to_public()
        self.node = node
        self.req = cloudscraper.create_scraper()
        self.wax = eospy.cleos.Cleos(url=node)

        self.name = self.GetName()

    def Contract(self, name: str, actor: str=None, force_recreate: bool=False, node: str=None):
        return Contract(name, self, actor=actor, force_recreate=force_recreate, node=node)

    def SetNode(self, node: str):
        self.node = node

    def GetName(self, permission="active"):
        """
        ## Returns wallet name by public key
        - Returns
          - `str` wallet name
        """

        r =  self.req.post(
            f"{self.node}/v1/chain/get_accounts_by_authorizers", 
            json={"keys": [self.public_key], "accounts": []}).json()["accounts"]
        for acc in r:
            if acc['permission_name'] == permission:
                return acc['account_name']
        else:
            return r[0]['account_name']
    
    def Transaction(self, *actions):
        """
        ## Create transaction object\n
        ### Example:\n
        ```python
        from litewax import Client, Contract
        client = Client(private_key="")

        contract = Contract(name="eosio.token")
        contract.set_actor(client.name)

        trx = client.Transaction(
            contract.transfer(
                _from = "wallet1",
                _to = "wallet2",
                amount = "1.0000 WAX",
                memo = "memo"
            )
        )

        trx.push() # -> hash
        ```
        
        - Returns
          - `TX` Object
        """

        return TX(self, *actions)

    def sign(self, trx: bytearray):
        return eospy.keys.EOSKey(self.private_key).sign(trx)

class TX:
    def __init__(self, client: Anchor, *actions):
        self.client = client
        self.actions = list(actions)
        self.actions.reverse()
        self.wax = client.wax
        self.sign = client.sign

    def pay_with(self, payer: str, network='mainnet'):
        return PayWith(self, payer, network)

    def get_trx_extend_info(self):
        """
        ## Returns transaction extend info\n
        (tx, packed_trx, serealized_trx, signatures)
        """
        transaction = {
            "actions": self.actions
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        chain_info, lib_info = self.wax.get_chain_lib_info()
        trx = Transaction(transaction, chain_info, lib_info)

        digest = sig_digest(trx.encode(), chain_info['chain_id'])
        # sign the transaction
        signatures = [self.sign(digest)]

        # build final trx
        final_trx = {
            'compression': 'none',
            'transaction': trx.__dict__,
            'signatures': signatures
        }
        data = json.dumps(final_trx, cls=EOSEncoder)

        return {
            "signatures": signatures,
            "packed": trx.encode().hex(),
            "serealized": [x for x in trx.encode()],
            "data": data
        }

    def push(self) -> Tuple[dict, bool]:
        info = self.get_trx_extend_info()
        data = info['data']

        return self.wax.post('chain.push_transaction', params=None, data=data, timeout=120)

if __name__ == "__main__":
    a = Anchor("5JJYyiPpopRaQs1o7wQE6X7X1V5mc1pcE6iXGLKCQ8YpdVfv7hL")
    from contracts.res_pink import res_pink
    contract = res_pink()
    contract.actor = a.GetName()

    tx = a.Transaction(
        contract.noop()
    )
    print(tx)
    print(tx.push())