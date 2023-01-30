from dataclasses import dataclass
import typing

CUSTOM_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"
class WAXPayer:
    """
    WAXPayer is a class for storing supported payers
    
    :key NEFTYBLOCKS: neftyblocks payer
    :type NEFTYBLOCKS: str
    
    :key ATOMICHUB: atomichub payer
    :type ATOMICHUB: str

    """
    NEFTYBLOCKS: str = "neftyblocks"
    ATOMICHUB: str = "atomichub"

    

@dataclass
class TransactionInfo:
    """
    TransactionInfo is a dataclass for storing transaction info
    
    :key signatures: signatures
    :type signatures: `typing.List[str]`

    :key packed: packed transaction
    :type packed: `str`

    :key serealized: serealized transaction
    :type serealized: `typing.List[int]`

    """
    signatures: typing.List[str]
    packed: str
    serealized: typing.List[int]