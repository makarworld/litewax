from dataclasses import dataclass

CUSTOM_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"
class Payers:
    NEFTY = "nefty"
    NEFTYBLOCKS = "nefty"
    NeftyBlocks = "nefty"
    nefty = "nefty"
    neftyblocks = "nefty"
    Nefty = "nefty"

    ATOMICHUB = "atomichub"
    ATOMIC_HUB = "atomichub"
    AtomicHub = "atomichub"
    atomichub = "atomichub"

    CUSTOM = "custom"
    Custom = "custom"
    custom = "custom"
    

@dataclass
class TransactionInfo:
    signatures: list
    packed: str
    serealized: list