from abigen import abigen

def Contract(name: str, client=None):
    abigen().gen(name)
    mod = __import__(f"contracts.{name.replace('.', '_')}", fromlist=[name.replace('.', '_')])
    klass = getattr(mod, name.replace('.', '_'))
    if client:
        return klass(actor=client.name)

    return klass()

if __name__ == "__main__":
    c = Contract("res.pink")
    c.set_actor("zknmi.wam")
    print(c.noop())