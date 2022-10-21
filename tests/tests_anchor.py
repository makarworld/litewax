import pytest
from dotenv import dotenv_values
ENV = dotenv_values(".env")

PVT_KEY = ENV.get("PVT_KEY")
COOKIE = ENV.get("COOKIE")

from requests.exceptions import HTTPError

from litewax import Anchor

def test_contract():
    anchor = Anchor(private_key=PVT_KEY)
    contract = anchor.Contract("eosio.token")

    from contracts.eosio_token import eosio_token

    assert isinstance(contract, eosio_token)
    assert contract.actor == "atonicmaiket"
    assert contract.permission == "active"
    assert contract.wax._prod_url == "https://wax.greymass.com"

def test_set_node():
    anchor = Anchor(private_key=PVT_KEY)

    assert anchor.node == "https://wax.greymass.com"

    anchor.SetNode('http://wax.pink.gg')

    assert anchor.node == "http://wax.pink.gg"

def test_get_name():
    anchor = Anchor(private_key=PVT_KEY)

    assert anchor.GetName() == "atonicmaiket"

def test_transaction_fail():
    anchor = Anchor(private_key=PVT_KEY)

    from litewax.anchor import TX

    trx = anchor.Transaction()

    assert isinstance(trx, TX)

    with pytest.raises(HTTPError):
        trx.push()


def test_transaction_good():
    anchor = Anchor(private_key=PVT_KEY)

    from litewax.anchor import TX

    trx = anchor.Transaction(
        anchor.Contract("res.pink").noop()
    )

    assert isinstance(trx, TX)

    res = trx.push()

    assert isinstance(res, dict)
    assert res.get("transaction_id") is not None




