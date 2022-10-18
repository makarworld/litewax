import cloudscraper
import eospy.cleos
import eospy.keys


from node import NODE
from exceptions import AuthNotFound

class Client():
    def __init__(self, private_key="", cookie="", node: str=NODE()):
        if not private_key and not cookie:
            raise AuthNotFound("You must provide either a private key or a cookie")
        
        if private_key:
            self.private_key = private_key
            self.public_key = eospy.keys.EOSKey(private_key).get_public_key()
            self.wax = eospy.cleos.Cleos(url=node, key_provider=private_key)

            self.type = "private_key"


