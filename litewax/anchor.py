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
from eospy.types import Transaction
from eospy.utils import sig_digest
from eospy.signer import Signer
from eospy.exceptions import EOSKeyError

import cloudscraper
import pytz
import datetime as dt

from .contract import Contract
from .wcw import TxConverter
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

        self.name = self.GetName()

    def Contract(self, name: str):
        return Contract(name, self)

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

        return TX(self, *actions, node=self.node)

    def sign(self, trx: bytearray):
        return eospy.keys.EOSKey(self.private_key).sign(trx)

class TX:
    def __init__(self, anchor: Anchor, *actions, node: str="https://wax.greymass.com"):
        self.anchor = anchor
        self.actions = list(actions)
        self.actions.reverse()
        self.wax = eospy.cleos.Cleos(url=node, version='v1')

    def get_trx_extra(self):
        tx = json.loads(self.sign())
        sigs = tx['signatures']

        tx = tx['transaction']
        tx['expiration'] = int(time.time() + 60)
        tx['max_net_usage_words'] = 0
        tx['max_cpu_usage_ms'] = 0

        return sigs, TxConverter(tx).bytes_list
    
    def get_trx_extend_info(self):
        """
        ## Returns transaction extend info\n
        (tx, packed_trx, serealized_trx, signatures)
        """
        sigs, TxByte = self.get_trx_extra()
        return {
            "signatures": sigs,
            "packed": TxByte.hex(),
            "serealized": [x for x in TxByte],
        }

    def get_packed_trx(self):
        return self.get_trx_extra().hex()
    
    def get_serealized_trx(self):
        return [x for x in self.get_trx_extra()]

    def sign(self):
        return self.push(broadcast=False)

    def push(self, broadcast=True) -> Tuple[dict, bool]:
        trx = {
            "actions": self.actions
        }
            
        trx['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        resp = self.wax.push_transaction(trx, eospy.keys.EOSKey(self.anchor.private_key), broadcast=broadcast)
        return resp

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