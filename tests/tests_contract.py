import pytest
import os

from litewax import Contract


def test_create_contract_good():
    contract = Contract("res.pink")

    assert os.path.exists('./contracts/res_pink.py')

    from contracts.res_pink import res_pink
    
    assert isinstance(contract, res_pink)

    with pytest.raises(ValueError):
        contract.noop()

    
    contract.set_actor("abuztradewax")

    assert contract.actor == "abuztradewax"

    noop = contract.noop()

    assert noop == {'account': 'res.pink', 'authorization': [{'actor': 'abuztradewax', 'permission': 'active'}], 'data': '', 'name': 'noop'}

def test_create_contract_bad():
    with pytest.raises(KeyError):
        contract = Contract("badcontract")

    assert not os.path.exists('./contracts/badcontract.py')

    with pytest.raises(ModuleNotFoundError):
        from contracts.badcontract import badcontract

