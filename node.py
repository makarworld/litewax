
import random


class nodes:
    # from https://wax.antelope.tools/nodes
    LIST = {
        "GRAYMASS" : "https://wax.greymass.com",
        "WAXSWEDEN" : "http://api.waxsweden.org",
        "PINK" : "http://wax.pink.gg",
        "EOSRIO" : "https://wax.eosrio.io",
        "EOSDAC" : "https://wax.eosdac.io",
        "NATION" : "http://wax.api.eosnation.io",
        "AMSTERDAMWAX" : "http://wax.eu.eosamsterdam.net",
        "BOUNTYBLOKBP" : "http://api.wax.bountyblok.io",
        "ALOHAEOS" : "http://api.wax.alohaeos.com",
        "EOSIODETROIT" : "http://api.wax.detroitledger.tech",
        "IVOTE4WAXUSA" : "http://wax.eosusa.io",
        "EOSPHEREIOBP" : "http://wax.eosphere.io",
        "SENTNLAGENTS1" : "http://hyperion5.sentnl.io",
        "SENTNLAGENTS2" : "http://hyperion2.sentnl.io",
        "WAXHIVEGUILD1" : "http://api.hivebp.io",
        "WAXHIVEGUILD2" : "http://api2.hivebp.io",
        "WAXHIVEGUILD3" : "http://wax.hivebp.io",
        "CRYPTOLIONS" : "http://wax.cryptolions.io"
    }

NODE = lambda: random.choice(list(nodes.LIST.values()))





