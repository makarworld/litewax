import os
from .abigen import abigen

def Contract(name: str, client=None, actor=None, permission="active", force_recreate=False, node=None):
    """
    ## Function for creating a contract object using wax abigen. 
    Contract objects will be saved in the contracts folder. 

    ### Parameters
    - `name`: The name of the contract (ex: res.pink)
    - `client`: A Client object (if actor is not provided)
    - `actor`: The actor name (if client is not provided)
    - `permission`: The permission to use (default: active)
    - `force_recreate`: Force the contract to be recreated (default: False)
    - `node`: The node to use (default: https://wax.greymass.com)

    ### Returns
    - `Contract`: A contract object
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

if __name__ == "__main__":
    c = Contract("res.pink")
    c.set_actor("zknmi.wam")
    print(c.noop())