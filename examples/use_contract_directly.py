# import library
from litewax import Client

# Create a client with a private key
client = Client(private_key="5K...")

# import contract object (for ex. eosio.token). Before you can use this contract, you must create a contract .py file via abigen. 
# For example, you can use this command: `python -c "from litewax import Contract; Contract('eosio.token')"`
from contracts.eosio_token import eosio_token

# init contract object
contract = eosio_token(actor=client.name)

# Create a transaction object
trx = client.Transaction(
    contract.transfer(
        _from=client.name,
        to="abuztradewax",
        quantity="1.00000000 WAX",
        memo="Test send"
    )
)

# Push the transaction
r = trx.push()

print(r)
# {'transaction_id': '928802d253bffc29d6178e634052ec5f044b2fcce0c4c8bc5b44d978e22ec5d4', ...}