from .wcw import WCW
from .anchor import Anchor
from .exceptions import AuthNotFound, NotImplementedError

class Client():
    """
    ## litewax.Client
    With this class you can send transactions.

    ### Example
    ```python
    from waxlite import Client, Contract

    client = Client(private_key="")

    # Last signed action will pay for all CPU
    trx = client.Transaction(
        Contract("eosio.token", client).transfer(
            _from = client.name,
            _to = "abuztradewax",
            amount = "1.0000 WAX",
            memo = "Send 1 WAX with litewax.Client"
        )
    )
    
    trx.push() # -> hash

    ```
    """

    def __init__(self, private_key="", cookie="", node: str='https://wax.greymass.com'):
        if not private_key and not cookie:
            raise AuthNotFound("You must provide either a private key or a cookie")
        
        if private_key and cookie:
            raise NotImplementedError("You can't use both private key and cookie")

        if private_key:
            self.private_key = private_key
            self.waxclient = Anchor(private_key, node=node)
            self.type = "private_key"

        elif cookie:
            self.cookie = cookie
            self.waxclient = WCW(cookie, node=node)
            self.type = "cookie"
        
        self.Transaction = self.waxclient.Transaction
        self.GetName = self.waxclient.GetName
        self.name = self.waxclient.name
    
    def SetNode(self, node: str):
        self.waxclient.SetNode(node)
        self.node = node
