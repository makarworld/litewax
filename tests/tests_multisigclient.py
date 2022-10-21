import pytest
from dotenv import dotenv_values
ENV = dotenv_values(".env")

PVT_KEY = ENV.get("PVT_KEY")
PVT_KEY1 = ENV.get("PVT_KEY1")
COOKIE = ENV.get("COOKIE")

from litewax import Anchor, MultiSigClient, client

from litewax.multisigclient import TX
from litewax.exceptions import AuthNotFound


def test_create_multisigclient_good():
    client = MultiSigClient(private_keys=[PVT_KEY, PVT_KEY1])
    assert isinstance(client, MultiSigClient) 

    assert client[0].name == "atonicmaiket"
    assert client[0].node == "https://wax.greymass.com"
    assert isinstance(client[0], Anchor)

    assert client[1].name == "abuztradewax"
    assert client[1].node == "https://wax.greymass.com"
    assert isinstance(client[1], Anchor)

def test_create_multisigclient_fail():
    with pytest.raises(AuthNotFound):
        MultiSigClient()


def test_create_trx_good():
    client = MultiSigClient(private_keys=[PVT_KEY, PVT_KEY1])

    tx = client.Transaction(
        client[0].Contract("res.pink").noop(),
        client[1].Contract("res.pink").noop()
    )
    assert isinstance(tx, TX)

    pushed_tx = tx.push()

    assert isinstance(pushed_tx, dict)
    assert pushed_tx["transaction_id"] is not None

#pytest.mark.parametrize("PVT_KEY, PVT_KEY1", [(PVT_KEY, PVT_KEY1), (PVT_KEY1, PVT_KEY)])
def test_transfer_token_2_to_1():
    client = MultiSigClient(private_keys=[PVT_KEY1, PVT_KEY])

    # send key1 -> key2

    tx = client.Transaction(
        client[0].Contract("eosio.token").transfer(
            _from=client[0].name, 
            to=client[1].name, 
            quantity="1.00000000 WAX", 
            memo=f"Test send {client[0].name} -> {client[1].name}"
        ),
        client[1].Contract("res.pink").noop()
    )

    r = tx.push()

    assert isinstance(r, dict)

def test_transfer_token_1_to_2():
    client = MultiSigClient(private_keys=[PVT_KEY, PVT_KEY1])

    # send key1 -> key2

    tx = client.Transaction(
        client[0].Contract("eosio.token").transfer(
            _from=client[0].name, 
            to=client[1].name, 
            quantity="1.00000000 WAX", 
            memo=f"Test send {client[0].name} -> {client[1].name}"
        ),
        client[1].Contract("res.pink").noop()
    )

    r = tx.push()

    assert isinstance(r, dict)

    