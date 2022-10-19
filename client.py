import cloudscraper
import eospy.cleos
import eospy.keys

from wcw import WCW
from anchor import Anchor
from exceptions import AuthNotFound

class Client():
    def __init__(self, private_key="", cookie="", node: str='https://wax.greymass.com'):
        if not private_key and not cookie:
            raise AuthNotFound("You must provide either a private key or a cookie")
        
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
        self.waxclient.node = node
        self.node = node
    


