import logging, os
from web3.auto import w3
from web3 import Web3
from secp256k1 import PrivateKey

def name():
    return 'transfer'

def subscribed_receipts(args):
    return {
        'type': 'tx',
        'value': b'hash',
    }

def db_namespace():
    return None

def init(args, context, db):
    context['nonce'] = 0
    context['txhash'] = None
    if 'priv_key' in args:
        context['priv_key'] = PrivateKey(bytes(bytearray.fromhex(args['priv_key'])), raw=True)
    else:
        context['priv_key'] = PrivateKey()

def run(args, context, db, receipts):
    logger = logging.getLogger('transfer.run')
    logger.debug('enter')
    if context['txhash'] != None and context['txhash'] not in receipts:
        logger.warn('Cannot find the receipt for last tx, waiting...')
        return []
    
    if context['txhash'] != None:
        receipt = receipts[context['txhash']]
        if receipt.status != 1:
            logger.warn('Transaction failed')

    to = os.urandom(20)
    tx = {
        'to': to,
        'value': 1,
        'gas': 21000,
        'gasPrice': 1,
        'nonce': context['nonce'],
        'data': b'',
    }
    tx = args['signer'](tx, context['priv_key'])

    context['nonce'] += 1
    context['txhash'] = tx['hash']
    logger.debug('before leaving')
    return [tx]
    