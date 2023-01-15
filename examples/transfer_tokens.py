from litewax import Client

# Create a client with a private key
client = Client(private_key="5K...")

# to - the account send the tokens to
to = "abuztradewax"

# Create a eosio.token contract object
contract = client.Contract("eosio.token")

# Create a transaction object
trx = client.Transaction(
    contract.transfer(
        _from=client.name,
        to=to,
        quantity="1.00000000 WAX",
        memo="Test send"
    )
)

# Push the transaction
r = trx.push()

print(r)