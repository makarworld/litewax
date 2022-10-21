from litewax import Client

# Create a client with a private key
client = Client(private_key="5K...")

# to - the account to send the tokens to
to = "abuztradewax"

# Create a atomicassets contract object
atomicassets = client.Contract("atomicassets")

# Create a atomicmarket contract object
atomicmarket = client.Contract("atomicmarket")

# Create a transaction object (https://wax.bloks.io/transaction/e6b2708b291bc2af06d95bfdad6fb65b71835c611b5c4228777d1ee602f4b9b4)
trx = client.Transaction( 
    atomicassets.createoffer(
        memo="sale",
        recipient="atomicmarket",
        recipient_asset_ids=[],
        sender=client.name,
        sender_asset_ids= ["1099608856151"]
    ),
    atomicmarket.announcesale(
        asset_ids=["1099608856151"],
        listing_price="100.00000000 WAX",
        maker_marketplace="",
        seller=client.name,
        settlement_symbol="8,WAX"
    )
)

# Push the transaction
r = trx.push()

print(r)

# Edit nft listing price (https://wax.bloks.io/transaction/37efdd4da70f97807fbf56efae5b438ba1a22ac7cce6224a4e33a020200cac00)
trx = client.Transaction(
    atomicmarket.cancelsale(
        sale_id="94472677"
    ),
    atomicassets.createoffer(
        memo="sale",
        recipient="atomicmarket",
        recipient_asset_ids=[],
        sender=client.name,
        sender_asset_ids= ["1099608856151"]
    ),
    atomicmarket.announcesale(
        asset_ids=["1099608856151"],
        listing_price="99.00000000 WAX",
        maker_marketplace="",
        seller=client.name,
        settlement_symbol="8,WAX"
    )
)

# Push the transaction
r = trx.push()

print(r)

# Cancel nft listing (https://wax.bloks.io/transaction/fec3677e2df0abc516d552d7fedfd9d9f1a0d702752843287904ec3c5dd59f3c)
trx = client.Transaction(
    atomicmarket.cancelsale(
        sale_id="97921174"
    )
)