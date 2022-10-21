from litewax import Client, Payers
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

print(trx.pay_with(Payers.NEFTY, network='testnet').push())