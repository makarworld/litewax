import cloudscraper
from .contract import Contract
from .exceptions import PayWithPushError
from eospy.utils import sig_digest
from .types import Payers
class AtomicHub:
    """
    Allowed actions:
    - atomicassets
    - atomicmarket

    """
    def __init__(self, trx, network="mainnet"):
        self.trx = trx
        self.wax = trx.client.wax

        if self.trx.actions[0]["account"] != "res.pink" or\
           self.trx.actions[0]["name"] != "noop" or\
           self.trx.actions[0]["authorization"][0]["actor"] != "res.pink" or\
           self.trx.actions[0]["authorization"][0]["permission"] != "paybw":
            
            self.trx.actions = [
                Contract("res.pink", actor="res.pink", permission="paybw").noop()
            ] + self.trx.actions

        self.scraper = cloudscraper.create_scraper(browser={'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})

        self.sign_link = "https://wax-mainnet-signer.api.atomichub.io/v1/sign"
        self.push_link = "chain.push_transaction"

    def push(self) -> dict:
        signed = self.trx.get_trx_extend_info()
        signatures = signed['signatures']

        # sign with atomichub
        self.scraper.options(self.sign_link, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "wax.api.atomicassets.io",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
        })

        sign_packed = self.scraper.post(self.sign_link, json={"transaction": signed['packed']}).json()

        if sign_packed.get('success') is False:
            raise PayWithPushError(sign_packed.get('message'))

        signatures += sign_packed['data']

        # push transaction
        push = self.wax.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed['packed']
        })
        return push


class Nefty:
    def __init__(self, trx, network="mainnet"):
        self.trx = trx
        self.wax = self.trx.wax

        if self.trx.actions[0]["account"] != "neftyblocksd" or\
           self.trx.actions[0]["name"] != "paycpu" or\
           self.trx.actions[0]["authorization"][0]["actor"] != "neftybrespay" or\
           self.trx.actions[0]["authorization"][0]["permission"] != "active":
            
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
        sign_packed = self.scraper.post(self.sign_link, json={"transaction": signed['packed']}).json()

        if sign_packed.get('error'):
            raise PayWithPushError(sign_packed['error'])

        signatures += sign_packed.json()['signatures']

        # push transaction
        push = self.wax.post(self.push_link, json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed['packed']
        })
        return push

class CustomPayer:
    def __init__(self, trx, payer_client, permission="active"):
        self.trx = trx
        self.wax = self.trx.wax
        self.payer_client = payer_client


        if self.trx.actions[0]["account"] != "res.pink" or\
           self.trx.actions[0]["name"] != "noop" or\
           self.trx.actions[0]["authorization"][0]["actor"] != payer_client.name or\
           self.trx.actions[0]["authorization"][0]["permission"] != permission:
            
            self.trx.actions = [
                Contract("res.pink", actor=payer_client.name, permission=permission).noop()
            ] + self.trx.actions

    def push(self) -> dict:
        signed = self.trx.get_trx_extend_info()
        signatures = signed['signatures']

        if self.payer_client.type == 'private_key':
            chain_info = self.trx.wax.get('chain.get_info')
            
            digest = sig_digest(bytearray(signed['serealized']), chain_info['chain_id'])

            signatures.append(self.payer_client.sign(digest))
        else:
            signatures += self.payer_client.sign(bytearray(signed['serealized']))

        # push transaction
        push = self.wax.post('chain.push_transaction', json={
            "signatures": signatures,
            "compression": 0,
            "packed_context_free_data": "",
            "packed_trx": signed['packed']
        })
        return push

class PayWith:
    def __init__(self, trx, pay_with="nefty", custom_payer_client=None, network="mainnet"):
        self.trx = trx
        if pay_with.lower() == "nefty":
            self.pay_with = Nefty(trx, network=network)

        elif pay_with.lower() == "atomichub":
            self.pay_with = AtomicHub(trx, network=network)

        elif pay_with.lower() == "custom":
            if not custom_payer_client:
                raise ValueError("You must specify custom_payer_client")
            self.pay_with = CustomPayer(trx, custom_payer_client)

        else:
            raise ValueError("Unknown payer. Must be 'Nefty', 'AtomicHub' or 'Custom'")

    def __str__(self):
        actions = ",\n\n        ".join([f"Action(account={x['account']}, name={x['name']}, authorization={x['authorization']}, data={x['data']})" for x in self.pay_with.trx.actions])
        return f"""litewax.Transaction(
    node={self.pay_with.trx.client.node},
    sender={self.pay_with.trx.client.name},
    actions=[
        {actions}
    ]
)"""

    def push(self):
        return self.pay_with.push()
