import blocksmith
from web3.auto import w3
from eth_hash.auto import keccak
from secp256k1 import PrivateKey

class Account:
    priv_key_hex = None
    priv_key = None

    def __init__(self, priv_key):
        self.priv_key_hex = priv_key
        self.priv_key = PrivateKey(bytes(bytearray.fromhex(priv_key)))

    def sign(self, tx):
        tx['v'] = 1
        tx['r'] = 0
        tx['s'] = 0

        unsigned_transaction = w3.eth.account.unsigned_transaction(tx)
        sig = self.priv_key.ecdsa_sign_recoverable(unsigned_transaction.hash(), raw=True)
        serialized, v = self.priv_key.ecdsa_recoverable_serialize(sig)
        r = int.from_bytes(serialized[:32], byteorder='big')
        s = int.from_bytes(serialized[32:], byteorder='big')
        raw = w3.eth.account.encode_signed_transaction(unsigned_transaction, vrs = (v+37, r, s))
        return raw, keccak(raw)

    def address(self):
        return blocksmith.EthereumWallet.generate_address(self.priv_key_hex)
