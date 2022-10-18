# litewax
Simply python library for iteract with WAX blockchain

# TODO
- [ ] Create Anchor client
- [x] Improve abigen
- [x] Create WCW client
- [ ] Edit path to save contracts files
- [ ] Create tests for WCW client
- [ ] Create MultiSig client
- [x] Add Contract function

# future example
```
>>> import litewax
>>> // Create client with private key(anchor)
>>> AnchorClient = litewax.Client(private_key=PVT_KEY)
>>>
>>> // Create client with token session(wax cloud wallet)
>>> WCWClient = litewax.Client(cookie=TOKEN_SESSION)
>>> 
>>> // Create multisig client (may accept wax cloud wallet and anchor)
>>> MultiClient = litewax.MultiSigClient(
        private_keys=[PVT_KEY1, PVT_KEY2, ...], 
        cookies=[TOKEN_SESSION1, TOKEN_SESSION2, ...]
    )
>>>
>>> // Create a contract object for iteract (file will be created in ./contracts/contract_file.py)
>>> contract = litewax.Contract(name="res.pink")
>>>
>>> // easy make transaction
>>> trx = AnchorClient.Transaction(
        contract.noop()
    )
>>> 
>>> // easy push transaction (if client is MultiSig, last signed action will pay for all cpu)
>>> trx.push()
>>> 0xabcd0123...
```