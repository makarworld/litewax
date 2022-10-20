import pytest
from dotenv import dotenv_values
from litewax import Client, Anchor, WCW
from litewax.exceptions import AuthNotFound, CookiesExpired

ENV = dotenv_values(".env")

PVT_KEY = ENV.get("PVT_KEY")
COOKIE = ENV.get("COOKIE")

def test_create_anchor_good():
    client = Client(private_key=PVT_KEY)
    assert isinstance(client, Client) 

    assert client.name == "atonicmaiket"
    assert client.node == "https://wax.greymass.com"
    assert client.type == "private_key"
    assert isinstance(client.waxclient, Anchor)

def test_create_wcw_good():
    client = Client(cookie=COOKIE)
    assert isinstance(client, Client) 

    assert client.name == "zknmi.wam"
    assert client.node == "https://wax.greymass.com"
    assert client.type == "cookie"
    assert isinstance(client.waxclient, WCW)

def test_create_fail():
    try:
        Client()
    except Exception as e:
        assert isinstance(e, AuthNotFound)

def test_bad_keys():
    try:
        Client(private_key="bad")
    except Exception as e:
        assert isinstance(e, ValueError)
    
    try:
        Client(cookie="badcookie")
    except Exception as e:
        assert isinstance(e, CookiesExpired)
    

    


