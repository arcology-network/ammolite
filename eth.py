from ammolite.contract import Contract

class Eth:

    def contract(self, **kwargs) -> Contract:
        return Contract(**kwargs)
