import cloudscraper
from .contract import Contract
from .exceptions import AtomicHubPushError, NeftyBlocksPushError
from .types import CUSTOM_BROWSER

# same interface as Transaction
class AtomicHub:
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
    __slots__ = ("__trx", "__client", "__scraper", "__sign_link", "__push_link")

    # client - MultiClient instance
    # trx - MulltiTransaction instance
    def __init__(self, client, trx, network="mainnet"):
        if network != "mainnet":
            raise NotImplementedError("Only mainnet is supported by AtomicHub")

        self.__trx = trx
        self.__client = client

        if self.__trx.actions[0].result["account"] != "res.pink" or\
           self.__trx.actions[0].result["name"] != "noop" or\
           self.__trx.actions[0].result["authorization"][0]["actor"] != "res.pink" or\
           self.__trx.actions[0].result["authorization"][0]["permission"] != "paybw":
            
            self.__trx.actions = [
                Contract("res.pink", actor="res.pink", permission="paybw").noop()
            ] + self.__trx.actions

        self.__scraper = cloudscraper.create_scraper(browser={'custom': CUSTOM_BROWSER})

        self.__sign_link = "https://wax-mainnet-signer.api.atomichub.io/v1/sign"
        self.__push_link = "chain.push_transaction"

    @property
    def trx(self):
        """
        :ref:`litewax.clients.MultiTransaction` instance
        """
        return self.__trx

    @trx.setter
    def trx(self, value):
        self.__trx = value

    @property
    def client(self):
        """
        :ref:`litewax.clients.MultiClient` instance
        """
        return self.__client

    @client.setter
    def client(self, value):
        self.__client = value

    @property
    def scraper(self):
        """
        CloudScraper instance
        """
        return self.__scraper

    @scraper.setter
    def scraper(self, value):
        self.__scraper = value

    @property
    def sign_link(self):
        """
        Link to sign transaction
        """
        return self.__sign_link

    @sign_link.setter
    def sign_link(self, value):
        self.__sign_link = value

    @property
    def push_link(self):
        """
        Link to push transaction
        """
        return self.__push_link

    @push_link.setter
    def push_link(self, value):
        self.__push_link = value

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
        if not signed:
            print(self.client)
            print(type(self.trx))
            signed = self.trx.prepare_trx(expiration = expiration)
        signatures = signed.signatures

        # sign with atomichub
        self.scraper.options(self.sign_link, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "wax.api.atomicassets.io",
            "Upgrade-Insecure-Requests": "1"
        })

        sign_packed = self.scraper.post(self.sign_link, json={"transaction": signed.packed}).json()

        if sign_packed.get('success') is False:
            raise AtomicHubPushError(sign_packed.get('message'))

        signatures += sign_packed['data']

        # push transaction
        push = self.client[0].wax.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed.packed
        })
        return push


class NeftyBlocks:
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
    __slots__ = ("__client", "__trx", "__scraper", "__sign_link", "__push_link")
    # client - MultiClient instance
    # trx - MulltiTransaction instance
    def __init__(self, client, trx, network="mainnet"):
        self.__client = client
        self.__trx = trx

        if self.__trx.actions[0].result["account"] != "neftyblocksd" or\
           self.__trx.actions[0].result["name"] != "paycpu" or\
           self.__trx.actions[0].result["authorization"][0]["actor"] != "neftybrespay" or\
           self.__trx.actions[0].result["authorization"][0]["permission"] != "active":
            
            self.__trx.actions = [
                Contract("neftybrespay", actor="neftybrespay").paycpu()
            ] + self.__trx.actions

        self.__scraper = cloudscraper.create_scraper()
        self.__scraper.headers.update({
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
        })

        self.__push_link = "chain.push_transaction"
        if network == "testnet":
            self.__sign_link = "https://cpu-test.neftyblocks.com/"
        
        elif network == "mainnet":
            self.__sign_link = "https://cpu.neftyblocks.com/"
        
        else:
            raise ValueError("Unknown network. Must be 'testnet' or 'mainnet'")

    @property
    def client(self):
        """
        :ref:`litewax.clients.MultiClient` instance
        """
        return self.__client

    @property
    def trx(self):
        """
        :ref:`litewax.clients.MultiTransaction` instance
        """
        return self.__trx

    @property
    def scraper(self):
        """
        Cloudscraper instance
        """
        return self.__scraper

    @property
    def sign_link(self):
        """
        Sign link
        """
        return self.__sign_link

    @property
    def push_link(self):
        """
        Push link
        """
        return self.__push_link

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
        if not signed:
            signed = self.trx.prepare_trx(expiration = expiration)
        signatures = signed.signatures

        # sign with neftyblocks
        self.scraper.options(self.sign_link)
        sign_packed = self.scraper.post(self.sign_link, json={"transaction": signed['packed']}).json()

        if sign_packed.get('error'):
            raise NeftyBlocksPushError(sign_packed['error'])

        signatures += sign_packed.json()['signatures']

        # push transaction
        push = self.client.wax.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed['packed']
        })
        return push

