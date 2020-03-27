from web3.auto import w3 

def sign_transaction(transaction_dict, priv_key):
    transaction_dict.pop('chainId', None)
    transaction_dict['v'] = 1
    transaction_dict['r'] = 0
    transaction_dict['s'] = 0

    unsigned_transaction = w3.eth.account.unsigned_transaction(transaction_dict)
    sig = priv_key.ecdsa_sign_recoverable(unsigned_transaction.hash(), raw=True)
    serialized, v = priv_key.ecdsa_recoverable_serialize(sig)
    r = int.from_bytes(serialized[:32], byteorder='big')
    s = int.from_bytes(serialized[32:], byteorder='big')
    return {
        'raw': w3.eth.account.encode_signed_transaction(unsigned_transaction, vrs = (v+37, r, s)),
        'hash': unsigned_transaction.hash(),
        'to': transaction_dict['to'],
    }
