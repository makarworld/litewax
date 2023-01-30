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
    :param trx: MultiTransaction instance
    :param network: network name (default: mainnet)

    :raise NotImplementedError: if network is not mainnet

    :return: :obj:`AtomicHub` instance
    """
    # client - MultiClient instance
    # trx - MulltiTransaction instance
    def __init__(self, client, trx, network="mainnet"):
        if network != "mainnet":
            raise NotImplementedError("Only mainnet is supported by AtomicHub")

        self.trx = trx
        self.client = client

        if self.trx.actions[0].result["account"] != "res.pink" or\
           self.trx.actions[0].result["name"] != "noop" or\
           self.trx.actions[0].result["authorization"][0]["actor"] != "res.pink" or\
           self.trx.actions[0].result["authorization"][0]["permission"] != "paybw":
            
            self.trx.actions = [
                Contract("res.pink", actor="res.pink", permission="paybw").noop()
            ] + self.trx.actions

        self.scraper = cloudscraper.create_scraper(browser={'custom': CUSTOM_BROWSER})

        self.sign_link = "https://wax-mainnet-signer.api.atomichub.io/v1/sign"
        self.push_link = "chain.push_transaction"

    def push(self, signed = {}, expiration = 180) -> dict:
        """
        Push transaction to blockchain with AtomicHub

        :param signed: signed transaction (default: {})
        :type signed: `dict`
        :param expiration: expiration time in seconds (default: 180)
        :type expiration: `int`

        :raise AtomicHubPushError: if transaction is not signed

        :return: :obj:`dict` with transaction data
        """
        if not signed:
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

        sign_packed = self.scraper.post(self.sign_link, json={"transaction": signed['packed']}).json()

        if sign_packed.get('success') is False:
            raise AtomicHubPushError(sign_packed.get('message'))

        signatures += sign_packed['data']

        # push transaction
        push = self.client[0].wax.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed['packed']
        })
        return push


class NeftyBlocks:
    """
    Pay for transaction with NeftyBlocks

    :param client: `litewax.MultiClient` instance
    :param trx: `litewax.MultiTransaction` instance
    :param network: network name (default: mainnet)

    :raise ValueError: if network is not mainnet or testnet

    :return: :obj:`NeftyBlocks` instance
    """
    # client - MultiClient instance
    # trx - MulltiTransaction instance
    def __init__(self, client, trx, network="mainnet"):
        self.client = client
        self.trx = trx

        if self.trx.actions[0].result["account"] != "neftyblocksd" or\
           self.trx.actions[0].result["name"] != "paycpu" or\
           self.trx.actions[0].result["authorization"][0]["actor"] != "neftybrespay" or\
           self.trx.actions[0].result["authorization"][0]["permission"] != "active":
            
            self.trx.actions = [
                Contract("neftybrespay", actor="neftybrespay").paycpu()
            ] + self.trx.actions

        self.scraper = cloudscraper.create_scraper()
        self.scraper.headers.update({
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

        self.push_link = "chain.push_transaction"
        if network == "testnet":
            self.sign_link = "https://cpu-test.neftyblocks.com/"
        
        elif network == "mainnet":
            self.sign_link = "https://cpu.neftyblocks.com/"
        
        else:
            raise ValueError("Unknown network. Must be 'testnet' or 'mainnet'")

    def push(self, signed = {}, expiration = 180) -> dict:
        """
        Push transaction to blockchain with NeftyBlocks

        :param signed: signed transaction (default: {})
        :type signed: `dict`
        :param expiration: expiration time in seconds (default: 180)
        :type expiration: `int`

        :raise NeftyBlocksPushError: if transaction is not signed

        :return: :obj:`dict` with transaction data
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

