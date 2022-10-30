import json
import cloudscraper
import eospy.cleos
import eospy.keys
from eospy.types import Transaction
from eospy.utils import sig_digest
import datetime as dt
import pytz


from .paywith import PayWith
from .contract import Contract
from .exceptions import (
    CPUlimit, CookiesExpired, 
    ExpiredTransaction, UnknownError
)


class Client:
    """
    ### Methods:
    - Transaction
    - Contract
    - GetName
    - SetNode
    - sign
    """
    def __init__(self, private_key="", cookie="", node="https://wax.greymass.com"):
        self.node = node
        self.session = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})
        self.wax = eospy.cleos.Cleos(url=node)

        if private_key:
            self.type = "private_key"
            self.private_key = eospy.keys.EOSKey(private_key)
            self.public_key = self.private_key.to_public() 
            self.GetName = self.__GetNameAnchor
            self.sign = self.__signAnchor

        
        elif cookie:
            self.type = "cookie"
            self.cookie = cookie
            self.GetName = self.__GetNameWCW
            self.sign = self.__signWCW


        self.name = self.GetName()


    def __str__(self):
        return f"Client(name={self.name}, type={self.type}, node={self.node})"

    def __GetNameAnchor(self, permission="active") -> str:
        """
        Get wallet name by public key
        """
        r =  self.session.post(
            f"{self.node}/v1/chain/get_accounts_by_authorizers", 
            json={"keys": [self.public_key], "accounts": []}).json()["accounts"]
        for acc in r:
            if acc['permission_name'] == permission:
                return acc['account_name']
        else:
            return r[0]['account_name']

    def __GetNameWCW(self) -> str:
        """
        Get wallet name by session_token
        """
        try:
            return self.session.get(
                "https://api-idm.wax.io/v1/accounts/auto-accept/login",
                headers={"origin":"https://wallet.wax.io"}, 
                cookies={'session_token': self.cookie}).json()["userAccount"]
        except KeyError:
            raise CookiesExpired("Session token is expired")
    
    def __signWCW(self, trx: bytearray) -> list:
        """
        Sign WCW type transaction
        """
        self.session.options(
            "https://public-wax-on.wax.io/wam/sign", 
            headers={"origin":"https://all-access.wax.io"}, 
            cookies={'session_token': self.cookie})

        signed = self.session.post(
            "https://public-wax-on.wax.io/wam/sign",
            headers={
                'origin': 'https://all-access.wax.io',
                'referer': 'https://all-access.wax.io/',
                'x-access-token': self.cookie,
                'content-type': 'application/json;charset=UTF-8',
            },
            json={
                "serializedTransaction": [x for x in trx], # to serialize
                "website": "wallet.wax.io",
                "description": "jwt is insecure",
                "freeBandwidth": True
            },
            timeout=120
        )

        signatures = signed.json()["signatures"]
        return signatures
    
    def __signAnchor(self, trx: bytearray) -> str:
        """
        Sign Anchor type transaction
        """
        return self.private_key.sign(trx)

    def Contract(self, name: str, actor: str=None, force_recreate: bool=False, node: str=None):
        """
        Create a contract object
        """
        return Contract(name, self, actor=actor, force_recreate=force_recreate, node=node)

    def SetNode(self, node: str):
        """
        Change node
        """
        self.wax = eospy.cleos.Cleos(url=node)
        self.node = node

    def Transaction(self, *actions):
        """
        Create a transaction object
        """
        return TX(self, *actions)

class TX:
    """
    ### Methods:
    - pay_with
    - get_trx_extend_info
    - push
    """
    def __init__(self, client: Client, *actions):
        self.client = client
        self.wax = client.wax
        self.sign = client.sign

        if not actions:
            raise ValueError("Transaction must have at least one action")

        self.actions = list(actions)
        self.actions.reverse()

    def __str__(self):
        actions = ",\n\n        ".join([f"Action(account={x['account']}, name={x['name']}, authorization={x['authorization']}, data={x['data']})" for x in self.actions])
        return f"""litewax.Transaction(
    node={self.client.node},
    sender={self.client.name},
    actions=[
        {actions}
    ]
)"""


    def pay_with(self, payer: str, custom_payer_client: Client=None, network='mainnet') -> PayWith:
        """Create a paywith object"""
        return PayWith(self, payer, custom_payer_client, network)

    def get_trx_extend_info(self):
        """
        Sign transaction and get extend info
        ### Returns:
        - `signatures`: List[str]
        - `packed_trx`: str
        - `serealized`: List[int]
        """
        transaction = {
            "actions": self.actions
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        chain_info, lib_info = self.wax.get_chain_lib_info()
        trx = Transaction(transaction, chain_info, lib_info)

        if self.client.type == "private_key":
            digest = sig_digest(trx.encode(), chain_info['chain_id'])
            signatures = [self.sign(digest)]
        else:
            signatures = self.sign(trx.encode())

        return {
            "signatures": signatures,
            "packed": trx.encode().hex(),
            "serealized": [x for x in trx.encode()]
        }

    def push(self):
        """
        Push transaction
        ### Returns:
        - dict
        """
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