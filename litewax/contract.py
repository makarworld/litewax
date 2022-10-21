import os
from .abigen import abigen

def Contract(name: str, client=None, actor=None, force_recreate=False, node=None):
    if not node and client:
        node = client.node
    else:
        node = "https://wax.greymass.com"
    
    
    if not os.path.exists(f'contracts/{name.replace(".", "_")}.py') or force_recreate:
        abigen().gen(name)

    mod = __import__(f"contracts.{name.replace('.', '_')}", fromlist=[name.replace('.', '_')])
    klass = getattr(mod, name.replace('.', '_'))
    if client:
        return klass(actor=client.name, node=node)
    elif actor:
        return klass(actor=actor, node=node)

    return klass(node=node)

if __name__ == "__main__":
    c = Contract("res.pink")
    c.set_actor("zknmi.wam")
    print(c.noop())