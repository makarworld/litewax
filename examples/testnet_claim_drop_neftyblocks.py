from litewax import Client, WAXPayer
from dotenv import dotenv_values

ENV = dotenv_values(".env")

# try to get free cpu from neftyblocks
client = Client(private_key=ENV["PVT_KEY_TESTNET"], node=ENV["NODE"])

neftyblocksd = client.Contract("neftyblocksd")

trx = client.Transaction(
    neftyblocksd.claimdrop(
        claimer=client.name,
        drop_id=2020,
        amount=1,
        intended_delphi_median=0,
        referrer="NeftyBlocks",
        country="GB",
        currency="0,NULL"
    ),
    neftyblocksd.assertprice(
        drop_id=2020,
        listing_price="0 NULL",
        settlement_symbol="0,NULL"
    )
)
# add neftyblocks as payer
trx = trx.payer(WAXPayer.NEFTYBLOCKS, network="testnet")

# push transaction
push_resp = trx.push()

print(push_resp)
# {'transaction_id': '928802d253bffc29d6178e634052ec5f044b2fcce0c4c8bc5b44d978e22ec5d4', ...}
