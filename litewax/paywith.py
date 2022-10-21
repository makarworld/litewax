"""
A class for pay for CPU transactions by other accounts such as AtomicHub, Nefty, etc.

future example:
from litewax import Client, Contract, Payers
from litewax import Contract

client = Client(private_key="")

neftyblocksd = client.Contract("neftyblocksd")
neftybrespay = client.Contract("neftybrespay")

trx = client.Transaction(
    neftyblocksd.claimdrop(
        claimer=client.name,
        drop_id=2020,
        amount=1,
        intended_delphi_median=0,
        referrer="NeftyBlocks",
        country="GB",
        currency="0,NULL"
    ),
    neftyblocksd.assertprice(
        drop_id=2020,
        listing_price="0 NULL",
        settlement_symbol="0,NULL"
    ),
    neftybrespay.paycpu()
)

trx.push(paywith=Payers.Nefty)

trx.push(paywith="Nefty")
#  or
# trx.push(paywith="Nefty")
#  or
# trx.paywith.Nefty.push()
#  or
# trx.pay_with(Payers.NEFTY)
#  or
# trx.push(paywith="Nefty")


"""
import cloudscraper

class Payers:
    NEFTY = "NEFTY"
    ATOMICHUB = "ATOMICHUB"

    def __call__(self):
        return [x for x in self.__dict__.values() if x.isupper()]


class Nefty:
    def __init__(self, trx, client, network="mainnet"):
        self.trx = trx
        self.client = client

        self.scraper = cloudscraper.create_scraper(browser={'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        self.scraper.headers.update({
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'access-control-request-headers': 'content-type',
            'access-control-request-method': 'POST',
            'cache-control': 'no-cache',
            'origin': 'https://test.neftyblocks.com',
            'pragma': 'no-cache',
            'referer': 'https://test.neftyblocks.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site'
        })

        if network == "testnet":
            self.sign_link = "https://cpu-test.neftyblocks.com/"
            self.push_link = "https://wax-testnet.neftyblocks.com/v1/chain/send_transaction"
        
        elif network == "mainnet":
            self.sign_link = "https://cpu.neftyblocks.com/"
            self.push_link = "https://wax.neftyblocks.com/v1/chain/send_transaction"
        
        else:
            raise ValueError("Unknown network. Must be 'testnet' or 'mainnet'")

    def push(self) -> dict:
        signed = self.trx.get_trx_extend_info()
        signatures = signed['signatures']

        # sign with neftyblocks
        self.scraper.options(self.sign_link)
        sign_packed = self.scraper.post(self.sign_link, json={"tx": signed['packed']})

        signatures += sign_packed.json()['signatures']

        # push transaction
        self.scraper.options(self.push_link)
        push = self.scraper.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed['packed']
        })
        return push


class PayWith:
    def __init__(self, trx, client, pay_with="Nefty", network="mainnet"):
        self.trx = trx
        self.client = client
        if pay_with.lower() == "nefty":
            self.pay_with = Nefty(trx, client, network=network)
    
    def push(self):
        return self.pay_with.push()



print('nefty' in Payers())