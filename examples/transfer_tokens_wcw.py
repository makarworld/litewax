from litewax import Client

# Create a client with a session token from https://wallet.wax.io/. Guide: https://litewax.readthedocs.io/en/latest/other/get_token_session.html
client = Client(cookie="V5cS...vhF3")

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