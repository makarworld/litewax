import os
import eospy.cleos
import eospy.keys
import requests

file_start = """import eospy.cleos
import eospy.keys
import pytz
import datetime as dt
from typing import Tuple

class {name}:
    def __init__(self, actor: str="", permission: str="active", node: str="https://wax.greymass.com"):
        self.wax = eospy.cleos.Cleos(url=node, version='v1')
        self.actor = actor
        self.permission = permission

    def set_actor(self, actor: str):
        self.actor = actor

    def generatePayload(self, account: str, name: str) -> dict:
        if self.actor == "":
            raise ValueError("actor is not set")
        return {
            "account": account,
            "name": name,
            "authorization": [{
                "actor": self.actor,
                "permission": self.permission,
            }],
        }

    def return_payload(self, payload, args) -> dict:
        data = self.wax.abi_json_to_bin(
            payload['account'], 
            payload['name'], 
            args
        )
        payload['data'] = data['binargs']
        return payload

    # ACTIONS"""

file_action = """
    def {action}(self, {args}) -> Tuple[dict, dict]:
        \"\"\"
        ## ACTION: {name}.{action}
        - Parametrs:
            {description}
        \"\"\"

        {action}_args = {genargs}
        {action}_base = self.generatePayload("{name}", "{action}")
        return self.return_payload({action}_base, {action}_args)

"""

file_final = """    # ACTIONS END

    def push_actions(self, private_key: str, *actions) -> Tuple[dict, bool]:
        trx = {
            "actions": list(actions)
        }
            
        trx['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        resp = self.wax.push_transaction(trx, eospy.keys.EOSKey(private_key), broadcast=True)
        return resp, True

    def create_trx(self, private_key: str, **actions) -> Tuple[dict, dict]:
        ac = []
        for k, v in actions.items():
            ac.append(eval(f'self.{k}({", ".join({v})})'))
        return self.push_actions(private_key, ac)

if __name__ == '__main__':
    contract = {name}(username="")
    contract.push_actions(
        "PRIVATE_KEY",
        contract.transfer(
            _from="",
            to="",
            memo="",
            symbol=""
        )
    )

"""

TYPES = {
    'name': 'str',
    'asset': 'str',
    'uint64': 'int',
    'uint32': 'int',
    'uint16': 'int',
    'uint8': 'int',
    'int64': 'int',
    'int32': 'int',
    'int16': 'int',
    'int8': 'int',
    'float64': 'float',
    'float32': 'float',
    'float128': 'float',
    'bool': 'bool',
    'string': 'str',
    'public_key': 'str',
    'signature': 'str'
}

def check_ban(text):
    banwords = {
        "from": "_from",
        "for": "_for"
    }

    if text not in banwords.keys():
        return text
    else:
        return banwords.get(text)

class abigen():
    def __init__(self):
        pass

    def gen(self, name):
        actions = self.get_abi(name)
        out = file_start
        for action in actions:
            if action['name'].isupper(): # it's a table
                continue

        for action in actions:
            amtext = file_action
            if action['name'].isupper(): # it's a table
                continue

            if action.get('fields', {}): 

                formargs = []
                for x in action.get('fields', {}):
                    formargs.append(f"{check_ban(x['name'])}: {TYPES.get(x['type'], 'str') if '[]' not in x['type'] else 'list'}")

                args = ', '.join(formargs)

                desc = '\n            '.join([f"- {x['name']}: {x['type']}" for x in action.get('fields', {})])

            else:
                args= ''
                desc = ''

            action_args = "{\n" + str(',\n'.join([f"            \"{x['name']}\": {check_ban(x['name'])}" for x in action.get('fields', {})])) + "\n        }"

            for text, target in [
                ['{action}', action['name']],
                ['{description}', desc],
                ['{args}', args],
                ['{name}', name],
                ['{genargs}', action_args]
            ]:
                amtext = amtext.replace(text, target)
            
            out += amtext

        out += file_final

        out = out.replace('{name}', name.replace('.', '_'))

        if not os.path.exists('contracts'):
            os.makedirs('contracts')

        with open('./contracts/' + name.replace('.', '_') + '.py', "w", encoding='utf-8') as f:
            f.write(out)
        return out
        
    def get_abi(self, account_name: str):
        r = requests.post("https://wax.eosn.io/v1/chain/get_abi", json={"account_name": account_name}).json()
        return r['abi']['structs']

    def get_tx_info(self, tx: str):
        return requests.post("https://wax.greymass.com/v1/history/get_transaction",
                   json={"id": tx, "block_num_hint": 0}).json()

if __name__ == "__main__":
    app = abigen()
    app.gen("res.pink")