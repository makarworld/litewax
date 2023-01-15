from litewax.client import Client
from litewax import WAXPayer

from dotenv import dotenv_values

ENV = dotenv_values(".env")

# try to get free cpu from atomichub
client = Client(
    private_key=ENV["PVT_KEY"],
    node="https://wax.pink.gg"
)

trx = client.Transaction(
    client.Contract("atomicdropsx").assertdrop(
        assets_to_mint_to_assert=[{"template_id":172121,"tokens_to_back":[]}],
        drop_id="63075",
        listing_price_to_assert="0.01 USD",
        settlement_symbol_to_assert="8,WAX"
    ),
    client.Contract("atomicdropsx").claimdrop(
        claim_amount="1",
        claimer="atonicmaiket",
        country="RU",
        drop_id="63075",
        intended_delphi_median="830",
        referrer="atomichub"
    ),
    client.Contract("eosio.token").transfer(
        _from="atonicmaiket",
        to="atomicdropsx",
        quantity="0.12048192 WAX",
        memo="deposit"
    )
)


trx = trx.payer(WAXPayer.ATOMICHUB) # atomichub pay your trx cpu only if you haven't enough wax staked in cpu
print(trx)
print(trx.push())