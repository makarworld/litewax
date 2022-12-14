from litewax import Client

# Create a client with a private key
client = Client(private_key="5K...")

# to - the account to send the tokens to
to = "abuztradewax"

# Create a atomicassets contract object
contract = client.Contract("atomicassets")

# Create a transaction object
trx = client.Transaction(
    contract.transfer(
        _from=client.name,
        to=to,
        asset_ids=["1099608856151"], # https://wax.atomichub.io/explorer/asset/1099608856151
        memo="Test send"
    )
)

# Push the transaction
r = trx.push()

print(r)