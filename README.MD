[![Github last commit date](https://img.shields.io/github/last-commit/makarworld/litewax.svg?label=Updated&logo=github&cacheSeconds=600)](https://github.com/makarworld/litewax/commits)
[![Total downloads](https://img.shields.io/github/downloads/makarworld/litewax/total.svg?label=Downloads&logo=github&cacheSeconds=600)](https://github.com/makarworld/litewax/releases)
[![License](https://img.shields.io/github/license/makarworld/litewax.svg?label=License&logo=apache&cacheSeconds=2592000)](https://github.com/makarworld/litewax/blob/main/LICENSE.txt)

[WAX donate](https://wax.atomichub.io/trading/token-transfer?partner=abuztradewax)

# litewax
Simply python library for interact with WAX blockchain

# TODO
- [x] Create Anchor client
- [x] Improve abigen
- [x] Create WCW client
- [x] Edit path to save contracts files
- [x] Add Contract function
- [x] Create MultiSig client
- [ ] Create tests for WCW client
- [ ] Create tests for Anchor client
- [ ] Create tests for MultiSig client
 
---

# Installation 
```
pip install litewax
```

---

# Clients examples
## Import
```
from litewax import Client, MultiSigClient, Contract
```
## Client setup
Anchor
```
client = Client(private_key="PVT_KEY")
```

Wax Cloud Wallet
```
client = Client(cookie="TOKEN_SESSION")
```

Anchor MultiSigClient
```
client = MultiSigClient(private_keys=["PVT_KEY1", "PVT_KEY2", ...])
```

Wax Cloud Wallet MultiSigClient
```
client = MultiSigClient(cookies=["TOKEN_SESSION1", "TOKEN_SESSION2", ...])
```

---

# Contract examples
## Contract initialize
Default
```
contract = Contract("name", actor="wallet")
```

With client
```
contract = client.Contract("name")

# In MultiSigClient:
# contract = client.Contract("name", client[0])
# contract = client[0].Contract("name")
# contract = client.Contract("name", actor=client[0].name)
```

After once init you can import contract directly
```
# Contract("res.pink")
from contracts.res_pink import res_pink

contract = res_pink("actor")
```

---

# Transactions
## Make transaction
```
contract = client.Contract("res.pink")

trx = client.Transaction(
    contract.noop(),
    # or
    contract.call('noop', {})
)
```
## Push transaction
```
trx.push() # -> hash
# 0x0123abc...
```

---

# Examples
## (Anchor) Client example 
```
>>> import litewax
>>>
>>> # Create client with private key(anchor)
>>> client = litewax.Client(private_key=PVT_KEY)
>>>
>>> # Create a contract object for iteract (file will be created in ./contracts/contract_file.py)
>>> contract = litewax.Contract("res.pink", client)
>>> # or
>>> # contract = client.Contract("res.pink")
>>> # or
>>> # contract = litewax.Contract("res.pink")
>>> # contract.set_actor(client.name) 
>>>
>>> # easy make transaction
>>> trx = client.Transaction(
        contract.noop()
    )
>>> 
>>> # easy push transaction
>>> trx.push()
>>> 0xabcd0123...
```
## (Wax Cloud Wallet) Client example 
```
>>> import litewax
>>>
>>> # Create client with token session (wax cloud wallet)
>>> client = litewax.Client(cookie=TOKEN_SESSION)
>>> 
>>> # Create a contract object for iteract (file will be created in ./contracts/contract_file.py)
>>> contract = litewax.Contract("res.pink", client)
>>> # or
>>> # contract = client.Contract("res.pink")
>>> # or
>>> # contract = litewax.Contract("res.pink")
>>> # contract.set_actor(client.name) 
>>>
>>> # easy make transaction
>>> trx = AnchorClient.Transaction(
        contract.noop()
    )
>>> 
>>> # easy push transaction
>>> trx.push()
>>> 0xabcd0123...
```
## (Anchor) MultiSigClient example 
```
>>> import litewax
>>> 
>>> # Create multisig client (may accept wax cloud wallet and anchor)
>>> multiclient = litewax.MultiSigClient(
        private_keys=[PVT_KEY1, PVT_KEY2, ...]
    )
>>>
>>> # Create a contract object for iteract (file will be created in ./contracts/contract_file.py)
>>> contract = litewax.Contract("res.pink", client)
>>> # or
>>> # contract = client[i].Contract("res.pink")
>>> # or
>>> # contract = litewax.Contract("res.pink")
>>> # contract.set_actor(client[i].name) 
>>>
>>> # easy make transaction
>>> trx = multiclient.Transaction(
        contract.transfer(
            _from=client[0].name,
            _to=client[1].name,
            amount="1.0000 WAX",
            memo="Send 1 WAX with multisig client"
        ),
        client[1].Contract("res.pink").noop() # for pay CPU
    )
>>> 
>>> # easy push transaction (if client is MultiSig, last signed action will pay for all cpu)
>>> trx.push()
>>> 0xabcd0123...
```
## (Wax Cloud Wallet) MultiSigClient example 
```
>>> import litewax
>>> 
>>> # Create multisig client (may accept wax cloud wallet and anchor)
>>> multiclient = litewax.MultiSigClient(
        cookies=[cookie1, cookie2, ...]
    )
>>>
>>> # Create a contract object for iteract (file will be created in ./contracts/contract_file.py)
>>> contract = litewax.Contract("res.pink", client)
>>> # or
>>> # contract = client[i].Contract("res.pink")
>>> # or
>>> # contract = litewax.Contract("res.pink")
>>> # contract.set_actor(client[i].name) 
>>>
>>> # easy make transaction
>>> trx = multiclient.Transaction(
        contract.transfer(
            _from=client[0].name,
            _to=client[1].name,
            amount="1.0000 WAX",
            memo="Send 1 WAX with multisig client"
        ),
        client[1].Contract("res.pink").noop() # for pay CPU
    )
>>> 
>>> # easy push transaction (if client is MultiSig, last signed action will pay for all cpu)
>>> trx.push()
>>> 0xabcd0123...
```
## Contract obj example 
```
>>> from litewax import Contract
>>>
>>> contract = Contract("res.pink")
>>> # contract = Contract("res.pink", actor="abuztradewax")
>>> # contract = Contract("res.pink", actor="abuztradewax", force_recreate=True)
>>> #
>>> # After create contract once, abigen create folder "contracts" and you can import directly
>>>
>>> from contracts.res_pink import res_pink 
>>> # in contract name "." replace to "_"
>>>
>>> contract = res_pink(actor="abuztradewax")
>>> # contract = res_pink()
>>> # contract.set_actor("abuztradewax")
>>>
>>> # you can push transaction without initialize any clients (push work only for anchor accounts)
>>> contract.push_actions(
        "PRIVATE_KEY",
        contract.noop()
    )
>>> 0x123abc...
>>> 
>>> # also you can send multiply signed trx
>>> contract1 = Contract("eosio.token", actor="wallet1")
>>> contract2 = Contract("res.pink", actor="wallet2")
>>> 
>>> contract1.push_actions(
        ["PRIVATE_KEY1", "PRICATE_KEY2"],
        contract1.transfer(
            _from=contract1.actor,
            _to=contract2.actor,
            amount="1.0000 WAX",
            memo="send 1 WAX without any client (only Contract instance)"
        ),
        contract2.noop() # this action will pay for CPU
>>> 0x123abc...
```