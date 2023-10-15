import pytest
import os

from litewax import Contract


def test_create_contract_good():
    contract = Contract("litewaxpayer")

    assert os.path.exists('./contracts/litewaxpayer.py'), "Contract file does not exist"

    from contracts.litewaxpayer import litewaxpayer
    
    assert isinstance(contract, litewaxpayer), "Contract is not litewaxpayer"

    with pytest.raises(ValueError):
        contract.noop()

    
    contract.set_actor("abuztradewax")

    assert contract.actor == "abuztradewax", "Actor does not match"

    noop = contract.noop()

    assert noop == {'account': 'litewaxpayer', 'authorization': [{'actor': 'abuztradewax', 'permission': 'active'}], 'data': '', 'name': 'noop'}, "Noop does not match"

def test_create_contract_bad():
    with pytest.raises(KeyError):
        contract = Contract("badcontract")

    assert not os.path.exists('./contracts/badcontract.py'), "Contract file exist"

    with pytest.raises(ModuleNotFoundError):
        from contracts.badcontract import badcontract

