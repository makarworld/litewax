from __future__ import annotations
from cloudscraper import CloudScraper
from typing import Any, Tuple, Callable, List
from eospy.types import Transaction as EosTransaction
from .baseclients import AnchorClient, WCWClient
import eospy.cleos
from dataclasses import dataclass
import typing

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

class PayerInterface:
    support_networks: List[str]
    payer_action: ContractInterface 
    sign_urls: dict
    headers: dict
    trx: EosTransaction
    client: MultiClientInterface
    scraper: CloudScraper
    sign_link: str
    push_link: str

    def __init__(self, client, trx, network: str = "mainnet") -> None: ...
    def push(self, signed = {}, expiration = 180) -> dict: ...

class ActionInterface:
    contract: ContractInterface
    action: str
    args: dict
    result: dict

    def __init__(self, contract: ContractInterface, action: str, args: dict) -> None: ...
    def __call__(self) -> dict: ...

class ContractInterface:
    actor: str
    wax: eospy.cleos.Cleos
    permission: str

    def __init__(self, actor: str = "", permission: str = "active", node: str = "https://wax.greymass.com") -> None: ...
    def set_actor(self, actor: str) -> None: ...
    def generatePayload(self, account: str, name: str) -> dict: ...
    def return_payload(self, payload, args) -> dict: ...
    def call(self, action: str, args: dict) -> dict: ...
    def push_actions(self, private_keys: Any, *actions) -> Tuple[dict, bool]: ...
    def create_trx(self, private_key: str, **actions) -> Tuple[dict, dict]: ...
    def __getattr__(self, __name: str) -> Callable[[str], ActionInterface]: ...


class ClientInterface:
    root: typing.Union[AnchorClient, WCWClient]
    node: str
    wax: eospy.cleos.Cleos
    name: str
    change_node: typing.Callable[[str], None]
    sign: typing.Callable[[EosTransaction], EosTransaction]

    def __init__(self, private_key: typing.Optional[str] = "", cookie: typing.Optional[str] = "", node: typing.Optional[str] = "https://wax.greymass.com") -> None: ...
    def __str__(self) -> str: ...
    def Contract(self, name: str, actor: typing.Optional[typing.Union[str, None]] = None, force_recreate: typing.Optional[bool] = False, node: typing.Optional[str] = None) -> ContractInterface: ...
    def Transaction(self, *actions: tuple[ActionInterface, ...]) -> TransactionInterface: ...

class TransactionInterface:
    client: ClientInterface
    actions: typing.List[ActionInterface]

    def __init__(self, client: ClientInterface, *actions: tuple[ActionInterface, ...]): ...
    def __str__(self) -> str: ...
    def payer(self, payer: typing.Union[ClientInterface, WAXPayer.ATOMICHUB, WAXPayer.NEFTYBLOCKS, str], permission: typing.Optional[str] = "active") -> typing.Union[MultiTransactionInterface, PayerInterface]: ...
    def pack(self, chain_info: typing.Optional[dict] = {}, lib_info: typing.Optional[dict] = {}, expiration: typing.Optional[int] = 180): ...
    def prepare_trx(self, chain_info: typing.Optional[dict] = {}, lib_info: typing.Optional[dict] = {}, expiration: typing.Optional[int] = 180) -> TransactionInfo: ...
    def push(self, data: typing.Optional[TransactionInfo] = {}, expiration: typing.Optional[int] = 180) -> dict: ...

class MultiClientInterface:
    clients: typing.List[ClientInterface]

    def __init__(self, 
                 private_keys: typing.Optional[typing.List[str]] = [], 
                 cookies: typing.Optional[typing.List[str]] = [],  
                 clients: typing.Optional[typing.List[ClientInterface]] = [], 
                 node: typing.Optional[str] = 'https://wax.greymass.com') -> None: ...
    def __str__(self) -> str: ...
    def change_node(self, node: str) -> None: ... 
    def __getitem__(self, index) -> ClientInterface: ...
    def __iter__(self) -> typing.Iterator[ClientInterface]: ...
    def __next__(self) -> ClientInterface: ...
    def append(self, client: ClientInterface) -> None: ...
    def sign(self, 
             trx: bytearray, 
             whitelist: typing.Optional[typing.List[str]] = [], 
             chain_id: typing.Optional[str] = None) -> typing.List[str]: ...
    def Transaction(self, *actions: tuple[ActionInterface, ...]) -> MultiTransactionInterface: ...

class MultiTransactionInterface:
    wax: eospy.cleos.Cleos
    client: MultiClientInterface
    actions: typing.List[ActionInterface]

    def __init__(self, client: MultiClientInterface, *actions: tuple[ActionInterface, ...]) -> None: ...
    def __str__(self) -> str: ...
    def payer(self, payer: typing.Union[ClientInterface, WAXPayer.ATOMICHUB, WAXPayer.NEFTYBLOCKS, str], permission: typing.Optional[str] = "active") -> typing.Union[MultiTransactionInterface, PayerInterface]: ...
    def pack(self, chain_info: typing.Optional[dict] = {}, lib_info: typing.Optional[dict] = {}, expiration: typing.Optional[int] = 180) -> TransactionInfo: ...
    def prepare_trx(self, chain_info: typing.Optional[dict] = {}, lib_info: typing.Optional[dict] = {}, expiration: typing.Optional[int] = 180) -> TransactionInfo: ...
    def push(self, data: typing.Optional[TransactionInfo] = {}, expiration: typing.Optional[int] = 180) -> dict: ...