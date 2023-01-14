import cloudscraper
import eospy.cleos
import eospy.keys
import eospy.dynamic_url

from .types import CUSTOM_BROWSER
from .exceptions import (
    CookiesExpired, 
)

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
        return self.wax.post('chain.get_accounts_by_authorizers', json={"keys": [self.public_key], "accounts": []})['accounts'][0]['account_name']

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
