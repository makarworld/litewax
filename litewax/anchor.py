"""
interface:
class Anchor:
    method GetName -> walletname
    method Transaction -> TX

class TX:
    method push -> hash
"""
from typing import Tuple
import eospy.cleos
import eospy.keys
import cloudscraper
import pytz
import datetime as dt

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
        self.actions = actions
        self.wax = eospy.cleos.Cleos(url=node, version='v1')
        self.sign = anchor.sign

    def push(self) -> Tuple[dict, bool]:
        trx = {
            "actions": list(self.actions)
        }
            
        trx['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        resp = self.wax.push_transaction(trx, eospy.keys.EOSKey(self.anchor.private_key), broadcast=True)
        return resp

if __name__ == "__main__":
    a = Anchor("5JJYyiPpopRaQs1o7wQE6X7X1V5mc1pcE6iXGLKCQ8YpdVfv7hL")
    from contracts.res_pink import res_pink
    contract = res_pink()
    contract.actor = a.GetName()

    tx = a.Transaction(
        contract.noop()
    )
    #tx = contract.push_actions(
    #    a.private_key,
    #    contract.noop()
    #)
    print(tx)
    print(tx.push())