import os
import requests

file_start = """from __future__ import annotations
import eospy.cleos
import eospy.keys
import pytz
import datetime as dt
from typing import Tuple, Any

class Action:
    \"\"\"
    Action class for calling actions. 
    In :meth:`result` contains the result of the action.

    :param contract: Contract object
    :type contract: object
    :param action: Action name
    :type action: str
    :param args: Action arguments
    :type args: dict

    \"\"\"

    __slots__ = ("contract", "action", "args", "result")

    def __init__(self, contract: {name}, action: str, args: dict):
        self.contract = contract
        self.action = action
        self.args = args

        self.result = self()
    
    @property
    def contract(self) -> {name}:
        \"\"\"
        Contract object

        :return:
        \"\"\"
        return self.contract

    @property
    def action(self) -> str:
        \"\"\"
        Action name

        :return:
        \"\"\"
        return self.action

    @property
    def args(self) -> dict:
        \"\"\"
        Action arguments

        :return:
        \"\"\"
        return self.args

    @property
    def result(self) -> dict:
        \"\"\"
        Result of the action

        :return: 
        \"\"\"

        return self.result

    def __str__(self):
        return f"[{self.contract.permission}] {self.contract.actor} > {name}::{self.action}({self.args})"
    
    def __repr__(self):
        return self.__str__()

    def __call__(self):
        return self.contract.call(self.action, self.args)

class {name}:
    \"\"\"
    {name} contract object

    :param actor: Account name
    :type actor: str
    :param permission: Permission name
    :type permission: str
    :param node: The node to use (default: https://wax.greymass.com)
    :type node: str

    \"\"\"
    __slots__ = ("wax", "actor", "permission")

    def __init__(self, actor: str="", permission: str="active", node: str="https://wax.greymass.com"):
        self.wax = eospy.cleos.Cleos(url=node, version='v1')
        self.actor = actor
        self.permission = permission

    @property
    def actor(self) -> str:
        \"\"\"
        Account name

        :return:
        \"\"\"
        return self.actor
    
    @actor.setter
    def actor(self, actor: str) -> None:
        self.actor = actor

    @property
    def permission(self) -> str:
        \"\"\"
        Permission name

        :return:
        \"\"\"

        return self.permission

    @permission.setter
    def permission(self, permission: str) -> None:
        self.permission = permission

    @property
    def wax(self) -> eospy.cleos.Cleos:
        \"\"\"
        Cleos instance

        :return:
        \"\"\"

        return self.wax

    def __str__(self):
        return f"{name}(actor={self.actor}, permission={self.permission}, node={self.wax.url})"

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
        # if args is empty, return payload
        if not args:
            payload['data'] = ''
            return payload
            
        data = self.wax.abi_json_to_bin(
            payload['account'], 
            payload['name'], 
            args
        )
        payload['data'] = data['binargs']
        return payload

    # ACTIONS
    def call(self, action: str, args: dict) -> dict:
        \"\"\"
        ## CALL ANY ACTION
        - Parametrs:
            - action: str
            - args: dict

        - Returns:
            - dict
        \"\"\"

        base = self.generatePayload("{normal_name}", action)

        return self.return_payload(base, args)

"""

file_action = """
    def {action}(self, {args}) -> dict:
        \"\"\"
        ## ACTION: {name}.{action}
        - Parametrs:
            {description}

        - Returns:
            - dict
        \"\"\"

        {action}_args = {genargs}
        return Action(self, "{action}", {action}_args)

"""

file_final = """    # ACTIONS END

    def push_actions(self, private_keys: Any, *actions) -> Tuple[dict, bool]:
        trx = {
            "actions": [a.result for a in list(actions)]
        }
            
        trx['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        if isinstance(private_keys, str):
            private_keys = eospy.keys.EOSKey(private_keys)

        elif isinstance(private_keys, list):
            private_keys = [eospy.keys.EOSKey(i) for i in private_keys]

        resp = self.wax.push_transaction(trx, private_keys, broadcast=True)
        return resp, True

    def create_trx(self, private_key: str, **actions) -> Tuple[dict, dict]:
        ac = []
        for k, v in actions.items():
            ac.append(eval(f'self.{k}({", ".join({v})})'))
        return self.push_actions(private_key, ac)

if __name__ == '__main__':
    contract = {name}(actor="")
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
    """
    abigen class for generating python classes from abi to interact with contracts

    :param node: wax node url

    :return: :class:`abigen` class
    """
    __slots__ = ('__node')

    def __init__(self, node: str="https://wax.greymass.com"):
        self.__node = node

    @property
    def node(self) -> str:
        """
        Node URL
        """
        return self.__node

    def gen(self, name: str) -> str:
        """
        Generate python class from abi

        :param name: contract name
        :type name: str

        :return: content of generated file
        :rtype: str
        """
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

        out = out.replace('{normal_name}', name)
        out = out.replace('{name}', name.replace('.', '_'))

        if not os.path.exists('contracts'):
            os.makedirs('contracts')

        with open('./contracts/' + name.replace('.', '_') + '.py', "w", encoding='utf-8') as f:
            f.write(out)
        return out
        
    def get_abi(self, account_name: str) -> dict:
        """
        Get contract abi from node

        :param account_name: contract name
        :type account_name: str

        :return: abi
        :rtype: dict
        """
        r = requests.post(f"{self.node}/v1/chain/get_abi", json={"account_name": account_name}).json()
        return r['abi']['structs']

    def get_tx_info(self, tx: str) -> dict:
        """
        # Depricated
        Get transaction info from node
        
        :param tx: transaction id
        :type tx: str
        
        :return: transaction info
        :rtype: dict
        """
        return requests.post(f"{self.node}/v1/history/get_transaction",
                   json={"id": tx, "block_num_hint": 0}).json()

#if __name__ == "__main__":
#    app = abigen()
#    app.gen("res.pink")