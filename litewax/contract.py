import typing
import os
from .abigen import abigen

def Contract(name: str, client: typing.Optional[typing.Any] = None, actor: typing.Optional[str] = None, permission: typing.Optional[str] = "active", force_recreate: typing.Optional[bool] = False, node: typing.Optional[str] = None) -> object:
    """
    Function for creating a contract object using wax abigen. 
    Contract objects will be saved in the contracts folder. 

    .. note::
    
        If you will pack your application to executable, generate the contracts before packing.


    :param name: The name of the contract (ex: res.pink)
    :type name: str
    :param client: A :class:`litewax.clients.Client` object (if actor is not provided)
    :type client: litewax.clients.Client
    :param actor: The actor name (if client is not provided)
    :type actor: str
    :param permission: The permission to use (default: active)
    :type permission: str
    :param force_recreate: Force the contract to be recreated (default: False)
    :type force_recreate: bool
    :param node: The node to use (default: https://wax.greymass.com)
    :type node: str

    :return: :obj:`Contract` object
    :rtype: object
    """
    if not node and client:
        node = client.node
    else:
        node = "https://wax.greymass.com"
    
    
    if not os.path.exists(f'contracts/{name.replace(".", "_")}.py') or force_recreate:
        abigen().gen(name)

    mod = __import__(f"contracts.{name.replace('.', '_')}", fromlist=[name.replace('.', '_')])
    klass = getattr(mod, name.replace('.', '_'))
    if client:
        return klass(actor=client.name, node=node, permission=permission)
    elif actor:
        return klass(actor=actor, node=node, permission=permission)

    return klass(node=node, permission=permission)

#if __name__ == "__main__":
#    c = Contract("res.pink")
#    c.set_actor("zknmi.wam")
#    print(c.noop())


class Action:
    """Example Action object for calling actions on a contract"""
    def __init__(self, contract: object, action: str, args: dict):
        self.contract = contract
        self.action = action
        self.args = args

        self.result = self()
    
    def __str__(self):
        return f"[{self.contract.permission}] {self.contract.actor} > {object}::{self.action}({self.args})"
    
    def __repr__(self):
        return self.__str__()

    def __call__(self):
        return self.contract.call(self.action, self.args)