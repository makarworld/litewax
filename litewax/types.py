from dataclasses import dataclass


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