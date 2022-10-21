# thanks for code https://github.com/lotusntp/Wax-Nefty
import cloudscraper
import eospy.cleos
from eospy.types import Transaction
import datetime as dt
import pytz

from .paywith import PayWith
from .contract import Contract
from .exceptions import CPUlimit, CookiesExpired, ExpiredTransaction, UnknownError

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"

def byteArrToArr(bArr)-> list:
    return [x for x in bArr]


class WCW:
    """WCW Client object\n
    methods:\n
    - Transaction(*actions) - create transaction object\n
    - Contract(name) - create contract object\n
    - SetNode(node) - set node\n
    - GetName() - get wallet name\n
    - sign(trx) - sign bytearray transaction\n
    """

    def __init__(self, session_token: str, node='https://wax.greymass.com'):
        self.session = cloudscraper.create_scraper(browser={'custom': USER_AGENT})
        self.wax = eospy.cleos.Cleos(url=node)
        self.session_token = session_token
        self.name = self.GetName()
        self.node = node

    def Contract(self, name: str):
        return Contract(name, self)
        
    def SetNode(self, node):
        self.wax = eospy.cleos.Cleos(url=node)
        self.node = node

    def GetName(self):
        try:
            return self.session.get(
                "https://api-idm.wax.io/v1/accounts/auto-accept/login",
                headers={"origin":"https://wallet.wax.io"}, 
                cookies={'session_token': self.session_token}).json()["userAccount"]
        except KeyError:
            raise CookiesExpired("Session token is expired")

    def Transaction(self, *actions):
        return TX(self, *actions)

    def sign(self, trx: bytearray):
        self.session.options(
            "https://public-wax-on.wax.io/wam/sign", 
            headers={"origin":"https://all-access.wax.io"}, 
            cookies={'session_token': self.session_token})

        signed = self.session.post(
            "https://public-wax-on.wax.io/wam/sign",
            headers={
                'origin': 'https://all-access.wax.io',
                'referer': 'https://all-access.wax.io/',
                'x-access-token': self.session_token,
                'content-type': 'application/json;charset=UTF-8',
            },
            json={
                "serializedTransaction": byteArrToArr(trx),
                "website": "wallet.wax.io",
                "description": "jwt is insecure",
                "freeBandwidth": True
            },
            timeout=120
        )

        signatures = signed.json()["signatures"]
        return signatures
        

class TX:
    """WCW Transaction object\n
    methods:\n
    - push() - push transaction to blockchain
    - get_trx_extend_info() - get transaction extended info
    """
    def __init__(self, client: WCW, *actions):
        self.wax = client.wax
        self.session_token = client.session_token
        if not actions:
            raise ValueError("Transaction must have at least one action")
        self.actions = list(actions)

        self.session = cloudscraper.create_scraper(browser={'custom': USER_AGENT})

        self.sign = client.sign
    
    def pay_with(self, payer: str, network='mainnet'):
        return PayWith(self, payer, network)

    def get_trx_extend_info(self):
        transaction = {
            "actions": self.actions
        }
            
        transaction['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        chain_info, lib_info = self.wax.get_chain_lib_info()
        trx = Transaction(transaction, chain_info, lib_info)


        return {
            "signatures": self.sign(trx.encode()),
            "packed": trx.encode().hex(),
            "serealized": [x for x in trx.encode()],
            "trx": trx
        }

    def push(self):
        info = self.get_trx_extend_info()
        signatures = info['signatures']
        packed = info['packed']

        push_tx = self.session.post(f"{self.wax._prod_url}/v1/chain/push_transaction",
            json={
                "signatures": signatures,
                "compression": 0,
                "packed_context_free_data": "",
                "packed_trx": packed
            },
            timeout=30
        )

        push_create_offer = push_tx.json()
        if push_create_offer['transaction_id'] == '':
            if push_create_offer['error']["what"] == 'Transaction exceeded the current CPU usage limit imposed on the transaction':
                raise CPUlimit('Error: CPU usage limit!!')

            elif push_create_offer['error']["what"] == 'Expired Transaction':
                raise ExpiredTransaction('Error: Expired Transaction!!')
            else:
                raise UnknownError(
                    f'Error: {push_create_offer["error"]["details"][0]["message"]}')

        return push_create_offer

if __name__ == "__main__":
    client = WCW("hY0u8DUYNXjucimdWDajkuX9cLGjNlNjukaV60JZ")
