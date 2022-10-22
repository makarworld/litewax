import cloudscraper
from .contract import Contract
from .exceptions import PayWithPushError
class Payers:
    NEFTY = "NEFTY"
    NEFTYBLOCKS = "NEFTY"
    NeftyBlocks = "NEFTY"

class Nefty:
    def __init__(self, trx, network="mainnet"):
        self.trx = trx

        if self.trx.actions[0]["account"] != "neftyblocksd" or\
           self.trx.actions[0]["name"] != "paycpu" or\
           self.trx.actions[0]["authorization"][0]["actor"] != "neftybrespay" or\
           self.trx.actions[0]["authorization"][0]["permission"] != "active":
            
            self.trx.actions = [Contract("neftybrespay", actor="neftybrespay").paycpu()] + self.trx.actions


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
        sign_packed = self.scraper.post(self.sign_link, json={"tx": signed['packed']}).json()

        if sign_packed.get('error'):
            raise PayWithPushError(sign_packed['error'])
        signatures += sign_packed.json()['signatures']

        # push transaction
        self.scraper.options(self.push_link)
        push = self.scraper.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed['packed']
        })
        return push.json()


class PayWith:
    def __init__(self, trx, pay_with="nefty", network="mainnet"):
        self.trx = trx
        if pay_with.lower() == "nefty":
            self.pay_with = Nefty(trx, network=network)
        else:
            raise ValueError("Unknown payer. Must be 'Nefty'")
    
    def push(self):
        return self.pay_with.push()
