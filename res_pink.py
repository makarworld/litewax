
import eospy.cleos
import eospy.keys
import pytz
import datetime as dt

class res_pink:
    def __init__(self, username: str, node: str="https://wax.greymass.com"):
        self.wax = eospy.cleos.Cleos(url=node, version='v1')
        self.username = username

    def generatePayload(self, account: str, name: str) -> dict:
        return {
            "account": account,
            "name": name,
            "authorization": [{
                "actor": self.username,
                "permission": "active",
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

    # ACTIONS
    def noop(self, ):
        """
        CONTRACT: res.pink
        ACTION: noop
        arguments: 
        """

        noop_args = {}
        noop_base = self.generatePayload("res.pink", "noop")
        return noop_args, noop_base

    # ACTIONS END

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
    contract = res_pink(username="")
    contract.push_actions(
        "",
        contract.transfer(
            _from="",
            to="",
            memo="",
            symbol=""
        )
    )

