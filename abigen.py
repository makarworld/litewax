import eospy.cleos
import eospy.keys
import requests

file_start = """
import eospy.cleos
import eospy.keys
import pytz
import datetime as dt

class {name}:
    def __init__(self, username: str, permission: str="active", node: str="https://wax.greymass.com"):
        self.wax = eospy.cleos.Cleos(url=node, version='v1')
        self.username = username
        self.permission = permission

    def generatePayload(self, account: str, name: str) -> dict:
        return {
            "account": account,
            "name": name,
            "authorization": [{
                "actor": self.username,
                "permission": self.permission,
            }],
        }

    def return_payload(self, payload, args):
        data = self.wax.abi_json_to_bin(
            payload['account'], 
            payload['name'], 
            args
        )
        payload['data'] = data['binargs']
        return payload

    # ACTIONS"""

file_action = """
    def {action}(self, {args}):
        \"\"\"
        ## ACTION: {name}.{action}
        - Parametrs:
        methods:
            {description}
        \"\"\"

        {action}_args = {genargs}
        {action}_base = self.generatePayload("{name}", "{action}")
        return {action}_args, {action}_base

"""

file_final = """    # ACTIONS END

    def push_actions(self, private_key: str, *actions):
        payloads = []
        for a in actions:
            payloads.append(self.return_payload(a[1], a[0]))

        trx = {
            "actions": payloads
        }
            
        trx['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        resp = self.wax.push_transaction(trx, eospy.keys.EOSKey(private_key), broadcast=True)
        return resp, True

    def create_trx(self, private_key: str, **actions):
        ac = []
        for k, v in actions.items():
            ac.append(eval(f'self.{k}({", ".join({v})})'))
        return self.push_actions(private_key, ac)

if __name__ == '__main__':
    contract = {name}(username="")
    contract.push_actions(
        "",
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
        out = file_start #.replace('{name}', name.replace('.', '_'))
        for action in actions:
            if action['name'].isupper(): # it's a table
                continue

        for action in actions:
            amtext = file_action
            if action['name'].isupper(): # it's a table
                continue

            if action.get('fields', {}): # FIX THIS SHIT
                args = ', '.join([f"{check_ban(x['name'])}: {TYPES.get(x['type'], 'str') if '[]' not in x['type'] else 'list'}" for x in action.get('fields', {})])
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

        out += file_final#.replace('{name}', name.replace('.', '_'))

        out = out.replace('{name}', name.replace('.', '_'))

        with open(name.replace('.', '_') + '.py', "w", encoding='utf-8') as f:
            f.write(out)
        return out

    def clone_by_name(self, name):
        actions = self.get_abi(name)
        out = file_start.replace('{name}', name.replace('.', '_'))

        for action in actions:
            amtext = file_action
            if action['name'].isupper(): # it's a table
                continue

            amtext = amtext.replace('{action}', action['name'])



            if action.get('fields', {}):
                args = ', '.join([f"{check_ban(x['name'])}: {TYPES.get(x['type'], 'str') if '[]' not in x['type'] else 'list'}" for x in action.get('fields', {})])
                
                desc = '\n            '.join([f"- {x['name']}: {x['type']}" for x in action.get('fields', {})])
            else:
                args= ''
                desc = ''
            
            amtext = amtext.replace('{description}', desc)

            amtext = amtext.replace('{args}', args)

            amtext = amtext.replace('{name}', name)

            action_args = ', '.join([f"\"{x['name']}\": {check_ban(x['name'])}" for x in action.get('fields', {})])
            amtext = amtext.replace('{genargs}', "{" + action_args + "}")
            
            out += amtext

        out += file_final.replace('{name}', name.replace('.', '_'))
        with open(name.replace('.', '_') + '.py', "w", encoding='utf-8') as f:
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
    app.gen("atomicdropsx")