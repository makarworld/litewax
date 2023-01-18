import pytest
import eospy.keys
from dotenv import dotenv_values
ENV = dotenv_values(".env")

PVT_KEY = ENV.get("PVT_KEY")
COOKIE = ENV.get("COOKIE")

from litewax import Client
from litewax.baseclients import WCWClient, AnchorClient
from litewax.exceptions import AuthNotFound, CookiesExpired

def test_create_anchor_good():
    client = Client(private_key=PVT_KEY)
    assert isinstance(client, Client) 

    assert client.name == "atonicmaiket", "Name does not match"
    assert client.node == "https://wax.greymass.com", "Node does not match"
    assert client.root.private_key == PVT_KEY, "Private key does not match"
    assert client.root.public_key == eospy.keys.EOSKey(PVT_KEY).get_public_key(), "Public key does not match"
    assert isinstance(client.root, AnchorClient), "Root is not AnchorClient"

def test_create_wcw_good():
    client = Client(cookie=COOKIE)
    assert isinstance(client, Client) 

    assert client.name == "zknmi.wam", "Name does not match"
    assert client.node == "https://wax.greymass.com", "Node does not match"
    assert client.root.cookie == COOKIE, "Cookie does not match"
    assert isinstance(client.root, WCWClient), "Root is not WCWClient"

def test_create_wrong_node():
    with pytest.raises(ValueError):
        Client(private_key=PVT_KEY, node="https://badnode.com")

def test_create_fail():
    with pytest.raises(ValueError):
        Client()

def test_bad_keys():
    with pytest.raises(ValueError):
        Client(private_key="bad")

    with pytest.raises(CookiesExpired):
        Client(cookie="badcookie")

    

    


