import pytest
from dotenv import dotenv_values
ENV = dotenv_values(".env")

PVT_KEY = ENV.get("PVT_KEY")
COOKIE = ENV.get("COOKIE")




from litewax import Client, Anchor, WCW
from litewax.exceptions import AuthNotFound, CookiesExpired

def test_create_anchor_good():
    client = Client(private_key=PVT_KEY)
    assert isinstance(client, Client) 

    assert client.name == "atonicmaiket"
    assert client.waxclient.node == "https://wax.greymass.com"
    assert client.type == "private_key"
    assert isinstance(client.waxclient, Anchor)

def test_create_wcw_good():
    client = Client(cookie=COOKIE)
    assert isinstance(client, Client) 

    assert client.name == "zknmi.wam"
    assert client.waxclient.utils.node == "https://wax.greymass.com"
    assert client.type == "cookie"
    assert isinstance(client.waxclient, WCW)

def test_create_fail():
    with pytest.raises(AuthNotFound):
        Client()

def test_bad_keys():
    with pytest.raises(ValueError):
        Client(private_key="bad")

    with pytest.raises(CookiesExpired):
        Client(cookie="badcookie")

    

    


