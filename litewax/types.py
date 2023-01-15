from dataclasses import dataclass

CUSTOM_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"
class WAXPayer:
    """
    ## WAXPayer is a class for storing supported payers
    
    ### Attributes:
         - NEFTYBLOCKS (str): neftyblocks
         - ATOMICHUB (str): atomichub
    """
    NEFTYBLOCKS = "neftyblocks"
    ATOMICHUB = "atomichub"

    

@dataclass
class TransactionInfo:
    """
    ## TransactionInfo is a dataclass for storing transaction info
    
    ### Attributes:
        - signatures (list): signatures
        - packed (str): packed transaction
        - serealized (list): serealized transaction
    """
    signatures: list
    packed: str
    serealized: list