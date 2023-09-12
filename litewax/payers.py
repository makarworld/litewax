import cloudscraper
from typing import List
from .contract import Contract
from .exceptions import PayerSignError
from .types import CUSTOM_BROWSER, ContractInterface, MultiClientInterface, MultiTransactionInterface


# same interface as Transaction
class CustomPayer:
    """
    Base for all payers
    """
    __slots__ = ("__trx", "__client", "__scraper", "__sign_link", "__push_link", "support_networks", "payer_action", "sign_urls")
    # example: ["mainnet", "testnet"]
    support_networks: List[str] = []
    # example: Contract("res.pink", actor="res.pink", permission="paybw").noop()
    payer_action: ContractInterface = None 
    # sign_url - url for sign transaction
    sign_urls: dict = dict(
        mainnet = "mainnet-url",
        testnet = "testnet-url"
    )
    # headers - custom headers for all requests
    headers: dict = {}

    # client - MultiClient instance
    # trx - MulltiTransaction instance
    def __init__(self, client: MultiClientInterface, trx: MultiTransactionInterface, network: str = "mainnet") -> None:
        if network not in self.support_networks:
            raise NotImplementedError(f"Network {network} is not supported by {self.__name__}. Supported networks: {self.support_networks}")

        self.__trx = trx
        self.__client = client

        if self.__trx.actions[0].result["account"] != self.payer_action["account"] or\
           self.__trx.actions[0].result["name"] != self.payer_action["account"] or\
           self.__trx.actions[0].result["authorization"][0]["actor"] != self.payer_action["authorization"][0]["actor"] or\
           self.__trx.actions[0].result["authorization"][0]["permission"] != self.payer_action["authorization"][0]["permission"]:
            
            self.__trx.actions = [self.payer_action] + self.__trx.actions

        self.__scraper = cloudscraper.create_scraper(browser={'custom': CUSTOM_BROWSER})
        self.__scraper.headers.update(self.headers)

        self.__sign_link = self.sign_urls[network]
        self.__push_link = "chain.push_transaction"

    @property
    def trx(self) -> MultiTransactionInterface:
        """
        :ref:`litewax.clients.MultiTransaction` instance
        """
        return self.__trx

    @trx.setter
    def trx(self, value):
        self.__trx = value

    @property
    def client(self) -> MultiClientInterface:
        """
        :ref:`litewax.clients.MultiClient` instance
        """
        return self.__client

    @client.setter
    def client(self, value):
        self.__client = value

    @property
    def scraper(self) -> cloudscraper.CloudScraper:
        """
        CloudScraper instance
        """
        return self.__scraper

    @scraper.setter
    def scraper(self, value):
        self.__scraper = value

    @property
    def sign_link(self) -> str:
        """
        Link to sign transaction
        """
        return self.__sign_link

    @sign_link.setter
    def sign_link(self, value):
        self.__sign_link = value

    @property
    def push_link(self) -> str:
        """
        Link to push transaction
        """
        return self.__push_link

    @push_link.setter
    def push_link(self, value):
        self.__push_link = value

    def push(self, signed = {}, expiration = 180) -> dict:
        """
        Push transaction to blockchain with payer link

        :param signed: signed transaction (default: {})
        :type signed: dict
        :param expiration: expiration time in seconds (default: 180)
        :type expiration: int

        :raise PayerSignError: if transaction is not signed

        :return: :obj:`dict` with transaction data
        :rtype: dict
        """
        if not signed:
            signed = self.trx.prepare_trx(expiration = expiration)

        signatures = signed.signatures

        sign_packed = self.scraper.post(self.sign_link, json = {"transaction": signed.packed}).json()

        if sign_packed.get('success') is False:
            raise PayerSignError(sign_packed.get('message'))

        signatures += sign_packed['data']

        # push transaction
        push = self.client[0].wax.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed.packed
        })
        return push


class AtomicHub(CustomPayer):
    """
    Pay for transaction with AtomicHub

    Allowed actions:
    - atomicassets
    - atomicmarket

    :param client: MultiClient instance
    :type client: :class:`litewax.clients.MultiClient`
    :param trx: MultiTransaction instance
    :type trx: :class:`litewax.clients.MultiTransaction`
    :param network: network name (default: mainnet)
    :type network: `str`

    :raise NotImplementedError: if network is not mainnet

    """
    support_networks: List[str] = ["mainnet"]
    payer_action: Contract = Contract("res.pink", actor="res.pink", permission="paybw").noop() 
    sign_urls = dict(
        mainnet = "https://wax-mainnet-signer.api.atomichub.io/v1/sign"
    )

    def push(self, signed = {}, expiration = 180) -> dict:
        """
        Push transaction to blockchain with AtomicHub

        :param signed: signed transaction (default: {})
        :type signed: dict
        :param expiration: expiration time in seconds (default: 180)
        :type expiration: int

        :raise AtomicHubPushError: if transaction is not signed

        :return: :obj:`dict` with transaction data
        :rtype: dict
        """
        return super().push(signed, expiration)


class NeftyBlocks(CustomPayer):
    """
    Pay for transaction with NeftyBlocks

    :param client: :class:`litewax.clients.MultiClient` instance
    :type client: litewax.clients.MultiClient
    :param trx: :class:`litewax.clients.MultiTransaction` instance
    :type trx: litewax.clients.MultiTransaction
    :param network: network name (default: mainnet)
    :type network: `str`

    :raise ValueError: if network is not mainnet or testnet

    """
    support_networks: List[str] = ["mainnet", "testnet"]
    payer_action: ContractInterface = Contract("neftybrespay", actor="neftybrespay").paycpu()
    sign_urls = dict(
        mainnet = "https://cpu.neftyblocks.com/",
        testnet = "https://cpu-test.neftyblocks.com/"
    )
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'access-control-request-headers': 'content-type',
        'access-control-request-method': 'POST',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site'
    }


    def push(self, signed = {}, expiration = 180) -> dict:
        """
        Push transaction to blockchain with NeftyBlocks

        :param signed: signed transaction (default: {})
        :type signed: `dict`
        :param expiration: expiration time in seconds (default: 180)
        :type expiration: `int`

        :raise NeftyBlocksPushError: if transaction is not signed

        :return: :obj:`dict` with transaction data
        :rtype: dict
        """
        return super().push(signed, expiration)
