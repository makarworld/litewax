from litewax import MultiClient, Contract

# Create a client with a private keys
client = MultiClient(private_keys=["5K1...", "5K2...", "5K3..."])

# Create the transaction
trx = client.Transaction(
    
    # Use a some contract action 1 
    Contract("eosio.token", client[0]).transfer(
        _from=client[0].name,
        to=client[1].name,
        quantity="1.00000000 WAX",
        memo="Test send"
    ),

    # Use a some contract action 2
    Contract("eosio.token", client[1]).transfer(
        _from=client[1].name,
        to=client[0].name,
        quantity="1.00000000 WAX",
        memo="Test send"
    ),

    # Sign last empty action for pay CPU. client[2] will pay for all transcation CPU
    Contract("res.pink", client[2]).noop()
)

# Push the transaction
r = trx.push()

print(r)
# {'transaction_id': '928802d253bffc29d6178e634052ec5f044b2fcce0c4c8bc5b44d978e22ec5d4', ...}