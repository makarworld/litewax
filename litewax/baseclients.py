import cloudscraper
import eospy.cleos
import eospy.keys
import eospy.dynamic_url
import typing 

from .exceptions import (
    CookiesExpired, 
)

CUSTOM_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"
class BaseClient:
    """
    BaseClient is a base client for interacting with the blockchain
    
    :param node: Node URL
    :type node: str
    
    :return:
    """
    __slots__ = ("__node", "__wax")

    def __init__(self, node: str) -> None:
        self.__node = node
        self.__wax = eospy.cleos.Cleos(url=node)
    
    @property
    def node(self) -> str:
        """
        Node URL
        """
        return self.__node

    @property
    def wax(self) -> eospy.cleos.Cleos:
        """
        Cleos instance
        """
        return self.__wax

    def change_node(self, node: str) -> None:
        """
        Change node for client by redeffining dynamic_url in `Cleos` instance
        
        :param node: Node URL
        :type node: str

        :return:
        """
        self.__node = node
        self.wax._prod_url = node
        self.wax._dynurl = eospy.dynamic_url.DynamicUrl(url=self.wax._prod_url, version=self.wax._version)

class AnchorClient(BaseClient):
    """
    AnchorClient is a client for interacting with the blockchain using a private key
    
    :param private_key: Private key string
    :type private_key: str
    :param node: Node URL
    :type node: str
    
    :return:
    """
    __slots__ = ("__private_key", "__public_key", "__name")

    def __init__(self, private_key: str, node: str) -> None:
        super().__init__(node)
        self.__private_key = eospy.keys.EOSKey(private_key)
        self.__public_key = self.private_key.to_public()
        self.__name = self.get_name()
    
    @property
    def private_key(self) -> eospy.keys.EOSKey:
        """
        Private key
        """
        return self.__private_key

    @property
    def public_key(self) -> eospy.keys.EOSKey:
        """
        Public key
        """
        return self.__public_key

    @property
    def name(self) -> str:
        """
        Wallet name
        """
        return self.__name

    def get_name(self) -> str:
        """
        Get wallet name by public key

        :raises: `KeyError` if account not found

        :return: wallet name
        :rtype: str
        """
        return self.wax.post('chain.get_accounts_by_authorizers', json={"keys": [self.public_key], "accounts": []})['accounts'][0]['account_name']

    def sign(self, trx: bytearray) -> typing.List[str]:
        """
        Sign transaction with private key

        :param trx: transaction to sign

        :return: signatures (length: 1)
        :rtype: list
        """
        return [self.private_key.sign(trx)]
    
class WCWClient(BaseClient):
    """
    WCWClient is a client for interacting with the blockchain using a WCW session token
    
    :param cookie: WCW session token
    :type cookie: str
    :param node: Node URL
    :type node: str
    
    :return:
    """
    __slots__ = ("__cookie", "__session", "__name")

    def __init__(self, cookie: str, node: str) -> None:
        super().__init__(node)
        self.__cookie = cookie
        self.__session = cloudscraper.create_scraper(browser={'custom': CUSTOM_BROWSER})
        self.__name = self.get_name()

    @property
    def cookie(self) -> str:
        """
        WCW session token
        """
        return self.__cookie

    @property
    def session(self) -> cloudscraper.CloudScraper:
        """
        CloudScraper instance
        """
        return self.__session

    @property
    def name(self) -> str:
        """
        Wallet name
        """
        return self.__name

    def get_name(self) -> str:
        """
        Get wallet name by session_token

        :raises: `litewax.exceptions.CookiesExpired` if session token is expired or invalid

        :return: wallet name
        :rtype: str
        """
        try:
            return self.session.get(
                "https://login-api.mycloudwallet.com/v1/wcw/session",
                headers={"origin":"https://www.mycloudwallet.com"}, 
                cookies={'session_token': self.cookie}).json()["account"]
        except KeyError:
            raise CookiesExpired("Session token is expired")

    def sign(self, trx: bytearray) -> typing.List[str]:
        """
        Sign transaction with WCW session token

        :param trx: transaction to sign
        :type trx: bytearray

        :return: signatures (length: 2)
        :rtype: list
        """
        self.session.options(
            "https://wax-on-api.mycloudwallet.com/wam/sign", 
            headers={"origin":"https://www.mycloudwallet.com"}, 
            cookies={'session_token': self.cookie})

        signed = self.session.post(
            "https://wax-on-api.mycloudwallet.com/wam/sign",
            headers={
                'origin': 'https://www.mycloudwallet.com',
                'referer': 'https://www.mycloudwallet.com',
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
        #print(signed.text)
        try:
            json_response = signed.json()
        except Exception as e:
            print(f"Error with signing transaction with WAX Cloud Wallet: {e}")

        if json_response.get("signatures") and json_response.get("serializedTransaction"):
            signatures = json_response["signatures"]
            _ = bytes(json_response["serializedTransaction"])

            return signatures
        else:
            raise ValueError("Invalid response while sign transaction with WAX Cloud Wallet: {}".format(signed.text))

