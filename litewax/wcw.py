# thanks for code https://github.com/lotusntp/Wax-Nefty
import json
import cloudscraper
from requests.exceptions import Timeout, ConnectionError, ChunkedEncodingError
import time
from json.decoder import JSONDecodeError

from .paywith import Payers, PayWith
from .contract import Contract
from .exceptions import CPUlimit, CookiesExpired, ExpiredTransaction, SessionExpired, SignError, UnknownError

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"

class utils:
    def __init__(self, node='https://wax.greymass.com', req=None):
        self.node = node
        if req:
            self.req = req
        else:
            self.req = cloudscraper.create_scraper(browser={'custom': USER_AGENT})


    def call(self, method: str, url: str, json: dict=None, headers: dict=None, timeout: int=30) -> dict:
        if not 'http' in url:
            # insert node to start of url
            if url[0] != '/':
                url = '/' + url

            url = f'{self.node}{url}'

        if method.upper() == "GET":
            info = self.req.get(url, json=json, headers=headers, timeout=timeout)

        elif method.upper() == "POST":
            info = self.req.post(url, json=json, headers=headers, timeout=timeout)

        return info


    def getcoin(self):
        try:
            info = self.call("POST",
                f"/v1/chain/get_table_rows",
                json={
                    "json": True,
                    "limit": 1,
                    "code": "delphioracle",
                    "scope": "waxpusd",
                    "table": "datapoints",
                    "index_position": 3,
                    "key_type": "i64",
                    "reverse": True,
                    "upper_bound": ""
                },
                timeout=30
            )
        except Exception as e:
            time.sleep(5)
            return self.getcoin()

        data = info.json()["rows"][0]
        return data

    def getBlock(self) -> dict:
        data = dict()
        try:
            info = self.call("GET", "/v1/chain/get_info")
            if info.status_code in [429, 502, 503, 504]:
                print('Get info data err. try again')
                time.sleep(1)
                return self.getBlock()
            data['ref_block_num'] = info.json()['head_block_num'] - 3
            # time.sleep(0.5)
            block = self.call("POST",
                f"/v1/chain/get_block",
                json={
                    "block_num_or_id": data['ref_block_num']
                },
                timeout=120
            )
            if block.status_code in [429, 502, 503, 504]:
                print('Get block data err. try again')
                time.sleep(1)
                return self.getBlock()
            try:
                data['ref_block_prefix'] = block.json()['ref_block_prefix']
            except:
                time.sleep(5)
                return self.getBlock()
        except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
            print('Connection(getblock) error. try again in 5 sec')
            time.sleep(5)
            return self.getBlock()
        return data


    def json_to_bin(self, obj: dict) -> str:
        try:
            bin = self.call("POST",
                "/v1/chain/abi_json_to_bin",
                json=obj,
                timeout=30
            )
            if bin.status_code not in [202, 200]:
                print('json_to_bin err. try again')
                print(f'code >>>>>>>>>>>>>>>>>>>{bin.status_code}')
                url = bin.url.split(".")
                print(
                    f'endpoint >>>>>>>>>>>>>>>>>>>{url[1] if len(url) == 3 else url[2]}')
                print(f'res >>>>>>>>>>>>>>>>>>>{bin.text}')
                time.sleep(3)
                return self.json_to_bin(obj)
            return bin.json()['binargs']
        except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
            print('Connection(json_to_bin) error. try again in 5 sec')
            time.sleep(5)
            return self.json_to_bin(obj)


    def pushTx(self, sign: list, tx: bytearray) -> dict:
        try:
            push_tx = self.call("POST",
                "/v1/chain/push_transaction",
                json={
                    "signatures": sign,
                    "compression": 0,
                    "packed_context_free_data": "",
                    "packed_trx": tx.hex()
                },
                timeout=30
            )
            if push_tx.status_code not in [202, 200]:
                if push_tx.status_code in [429, 502, 503, 504]:
                    print('Push Tx err. try again')
                    print(f'code >>>>>>>>>>>>>>>>>>>{push_tx.status_code}')
                    url = push_tx.url.split(".")
                    print(
                        f'endpoint >>>>>>>>>>>>>>>>>>>{url[1] if len(url) == 3 else url[2]}')
                    print(f'res >>>>>>>>>>>>>>>>>>>{push_tx.text}')
                    return self.pushTx(sign, tx)
                try:
                    err = push_tx.json()["error"]  # ["what"]
                    print(f'url {push_tx.url}')
                    return {
                        'error': err,
                        'transaction_id': ''
                    }
                except:
                    print('push err')
                    print(f'code >>>>>>>>>>>>>>>>>>>{push_tx.status_code}')
                    url = push_tx.url.split(".")
                    print(
                        f'endpoint >>>>>>>>>>>>>>>>>>>{url[1] if len(url) == 3 else url[2]}')
                    print(f'res >>>>>>>>>>>>>>>>>>>{push_tx.text}')
                    return self.pushTx(sign, tx)
            return push_tx.json()
        except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
            print('Connection(pushTx) error. try again in 5 sec')
            time.sleep(5)
            return self.pushTx(sign, tx)


    def byteArrToArr(self, bArr)-> list:
        return [x for x in bArr]


class TxConverter(object):


    def __init__(self, params):
        self.bytes_list = bytearray()

        self.push_int(params["expiration"] & 0xFFFFFFFF)
        self.push_short(params["ref_block_num"] & 0xFFFF)
        self.push_int(params["ref_block_prefix"] & 0xFFFFFFFF)
        self.push_variableUInt(params["max_net_usage_words"])
        self.push_variableUInt(params["max_cpu_usage_ms"])
        self.push_variableUInt(params["delay_sec"])
        self.push_actiones(list())  # TODO packfreedata
        self.push_actiones(params["actions"])
        self.push_variableUInt(0)  # TODO packexdata

    def char_to_symbol(self, c):
        if (ord(c) >= ord('a') and ord(c) <= ord('z')):
            return chr(((ord(c) - ord('a')) + 6))

        if (ord(c) >= ord('1') and ord(c) <= ord('5')):
            return chr(((ord(c) - ord('1')) + 1))
        return chr(0)

    def type_name_to_long(self, type_name):
        if type_name == None or type_name == "":
            return 0
        c = 0
        value = 0
        type_name_len = len(type_name)
        for i in range(12 + 1):
            if (i < type_name_len and i <= 12):
                c = ord(self.char_to_symbol(type_name[i]))
            if (i < 12):
                c &= 0x1f
                c <<= 64 - 5 * (i + 1)
            else:
                c &= 0x0f
            value |= c
        return value

    def push_base(self, val, iteration):
        for i in iteration:
            self.bytes_list.append(0xFF & val >> i)

    def push_short(self, val):
        self.push_base(val, range(0, 9, 8))

    def push_int(self, val):
        self.push_base(val, range(0, 25, 8))

    def push_long(self, val):
        self.push_base(val, range(0, 57, 8))

    def push_char(self, val):
        self.bytes_list.append(int(val))

    def push_variableUInt(self, val):
        b = int((val) & 0x7f)
        val = val >> 7
        b = b | (((val > 0) if 1 else 0) << 7)
        self.push_char(b)
        while val:
            b = int((val) & 0x7f)
            val = val >> 7
            b = b | (((val > 0) if 1 else 0) << 7)
            self.push_char(b)

    def push_actiones(self, val_list):
        self.push_variableUInt(len(val_list))
        for i in val_list:
            self.push_long(self.type_name_to_long(i["account"]))
            self.push_long(self.type_name_to_long(i["name"]))
            self.push_permission(i["authorization"])
            if i["data"]:
                self.push_data(i["data"])
            else:
                self.push_variableUInt(0)

    def push_permission(self, val_list):
        self.push_variableUInt(len(val_list))
        for i in val_list:
            self.push_long(self.type_name_to_long(i["actor"]))
            self.push_long(self.type_name_to_long(i["permission"]))

    def push_data(self, val):
        bytes = bytearray.fromhex(val)
        self.push_variableUInt(len(bytes))
        for i in bytes:
            self.bytes_list.append(i)

    def push_transaction_extensions(self, val_list):
        self.push_variableUInt(len(val_list))


class WCW:
    """WCW Client object\n
    methods:\n
    - Transaction(*actions) - create transaction object\n"""

    def __init__(self, session_token: str, node='https://wax.greymass.com'):
        self.session = cloudscraper.create_scraper(browser={'custom': USER_AGENT})
        self.utils = utils(node=node, req=self.session)
        self.session_token = session_token
        self.name = self.GetName()
        self.node = node

    def Contract(self, name: str):
        return Contract(name, self)
        
    def SetNode(self, node):
        self.utils.node = node
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
        """
        ## Create transaction object\n
        ### Example:\n
        ```python
        from litewax import Client, Contract
        client = Client(cookie="")

        contract = Contract(name="eosio.token")
        contract.set_actor(client.name)

        trx = client.Transaction(
            contract.transfer(
                _from = "wallet1",
                _to = "wallet2",
                amount = "1.0000 WAX",
                memo = "memo"
            )
        )

        trx.push() # -> hash
        ```

        - Returns
          - `TX` Object
        """
        block_data = self.utils.getBlock()

        tx = TxConverter({
            "expiration": int(time.time() + 60),
            "ref_block_num": block_data['ref_block_num'],
            "ref_block_prefix": block_data['ref_block_prefix'],
            "max_net_usage_words": 0,
            "max_cpu_usage_ms": 0,
            "delay_sec": 0,
            "context_free_actions": [],
            "actions": list(actions),
            "transaction_extensions":[]
        }).bytes_list

        return TX(self, tx)

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
                "serializedTransaction": self.utils.byteArrToArr(trx),
                "website": "wallet.wax.io",
                "description": "jwt is insecure",
                "freeBandwidth": True
            },
            timeout=120
        )
        if signed.status_code in [429, 502, 503, 504]:
            raise ConnectionError("Sign createOffer Tx Server err. try again")

        if signed.status_code == 403:
            raise ConnectionError("Sign createOffer tx CF 1020. try again in 30 sec\n" + signed.text)

        if signed.status_code != 200:
            try:
                if signed.json()['message'] == 'Recaptcha token is invalid.':
                    raise ConnectionError(f"{signed.json()['message']}\ntry to solve Recaptcha again...")
                
                elif signed.json()['message'] == 'Session Token is invalid or missing.':
                    raise SessionExpired(f'Sender Session Token is invalid or expire (token{self.session_token})')
                
                else:
                    raise UnknownError(signed.json())

            except:
                raise SignError(f'sign error:\n'\
                    f'code >>>>>>>>>>>>>>>>>>>{signed.status_code}\n'\
                    f'res >>>>>>>>>>>>>>>>>>>{signed.text}')

        signatures = signed.json()["signatures"]
        return signatures

class TX:
    """WCW Transaction object\n
    methods:\n
    - push() - push transaction to blockchain"""

    def __init__(self, client: WCW, tx: bytearray):
        self.utils = client.utils
        self.session_token = client.session_token
        self.tx = tx
        self.sign = client.sign

        self.session = cloudscraper.create_scraper(browser={'custom': USER_AGENT})
    
    def pay_with(self, payer: str):
        if payer.upper() not in Payers():
            raise ValueError(f"payer must be in {Payers()}")

        return PayWith(self, self.client, payer)

    def get_trx_extend_info(self):
        """
        ## Returns transaction extend info\n
        (signatures, packed, serealized)
        """
        return {
            "signatures": self.sign(),
            "packed": self.tx.hex(),
            "serealized": [x for x in self.tx],
        }

    def get_packed_trx(self):
        return self.tx.hex()
    
    def get_serealized_trx(self):
        return [x for x in self.tx]

    def sign(self):
        return self.client.sign(self.tx)

    def push(self):
        signatures = self.sign()
        
        push_create_offer = self.utils.pushTx(signatures, self.tx)
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
