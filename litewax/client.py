import cloudscraper
import eospy.cleos
import eospy.keys
import eospy.dynamic_url
from eospy.types import Transaction
from eospy.utils import sig_digest
import datetime as dt
import pytz

from .types import TransactionInfo
from .paywith import PayWith
from .contract import Contract
from .exceptions import (
    CPUlimit, CookiesExpired, 
    ExpiredTransaction, UnknownError
)
CUSTOM_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"
class BaseClient:
    """BaseClient is a base client for interacting with the blockchain"""
    __slots__ = ("node", "wax")

    def __init__(self, node: str) -> None:
        """Init a base client for interacting with the blockchain"""
        self.node = node
        self.wax = eospy.cleos.Cleos(url=node)
    
    def change_node(self, node: str) -> None:
        self.node = node
        self.wax._prod_url = node
        self.wax._dynurl = eospy.dynamic_url.DynamicUrl(url=self.wax._prod_url, version=self.wax._version)

class AnchorClient(BaseClient):
    """AnchorClient is a client for interacting with the blockchain using a private key"""
    __slots__ = ("private_key", "public_key", "name")

    def __init__(self, private_key: str, node: str) -> None:
        """Init a client for interacting with the blockchain using a private key"""
        super().__init__(node)
        self.private_key = eospy.keys.EOSKey(private_key)
        self.public_key = self.private_key.to_public()
        self.name = self.get_name()
    
    def get_name(self) -> str:
        """
        ## Get wallet name by public key
        
        Returns:
            - str: wallet name
        """
        return self.wax.get('chain.get_accounts_by_authorizers', {"keys": [self.public_key], "accounts": []})['accounts'][0]['account_name']

    def sign(self, trx: bytearray) -> list:
        """
        ## Sign transaction with private key

        Args:
            - trx (bytearray): transaction to sign

        Returns:
            - list: signatures (length: 1)
        """
        return [self.private_key.sign(trx)]
    
class WCWClient(BaseClient):
    """WCWClient is a client for interacting with the blockchain using a WCW session token"""
    __slots__ = ("cookie", "session", "name")

    def __init__(self, cookie: str, node: str) -> None:
        """Init a client for interacting with the blockchain using a WCW session token"""
        super().__init__(node)
        self.cookie = cookie
        self.session = cloudscraper.create_scraper(browser={'custom': CUSTOM_BROWSER})
        self.name = self.get_name()

    def get_name(self) -> str:
        """
        ## Get wallet name by session_token

        Returns:
            - str: wallet name
        """
        try:
            return self.session.get(
                "https://api-idm.wax.io/v1/accounts/auto-accept/login",
                headers={"origin":"https://wallet.wax.io"}, 
                cookies={'session_token': self.cookie}).json()["userAccount"]
        except KeyError:
            raise CookiesExpired("Session token is expired")

    def sign(self, trx: bytearray) -> list:
        """
        ## Sign transaction with WCW session token

        Args:
            - trx (bytearray): transaction to sign

        Returns:
            - list: signatures (length: 2)
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
        trx = Transaction(transaction, chain_info, lib_info)

        if isinstance(self.client.root, AnchorClient):
            digest = sig_digest(trx.encode(), chain_info['chain_id'])
            signatures = self.client.sign(digest)
        else:
            signatures = self.client.sign(trx.encode())

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