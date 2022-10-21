import pytest
from dotenv import dotenv_values
ENV = dotenv_values(".env")

PVT_KEY = ENV.get("PVT_KEY")
COOKIE = ENV.get("COOKIE")

from requests.exceptions import ConnectionError

from litewax import WCW

def test_contract():
    wcw = WCW(session_token=COOKIE)
    contract = wcw.Contract("eosio.token")

    from contracts.eosio_token import eosio_token

    assert isinstance(contract, eosio_token)
    assert contract.actor == "zknmi.wam"
    assert contract.permission == "active"
    assert contract.wax._prod_url == "https://wax.greymass.com"

def test_set_node():
    wcw = WCW(session_token=COOKIE)

    assert wcw.utils.node == "https://wax.greymass.com"

    wcw.SetNode('http://wax.pink.gg')

    assert wcw.utils.node == "http://wax.pink.gg"

def test_get_name():
    wcw = WCW(session_token=COOKIE)

    assert wcw.GetName() == "zknmi.wam"

def test_transaction_fail():
    wcw = WCW(session_token=COOKIE)

    from litewax.wcw import TX

    trx = wcw.Transaction()

    assert isinstance(trx, TX)

    with pytest.raises(ConnectionError):
        trx.push()


def test_transaction_good():
    wcw = WCW(session_token=COOKIE)

    from litewax.wcw import TX

    trx = wcw.Transaction(
        wcw.Contract("res.pink").noop()
    )

    assert isinstance(trx, TX)

    res = trx.push()

    assert isinstance(res, dict)
    assert res.get("transaction_id") is not None




