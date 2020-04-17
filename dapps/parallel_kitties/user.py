
import logging
from secp256k1 import PrivateKey
from web3.auto import w3
from dapps.parallel_kitty.utils import create_new_bid

def name():
    return 'pk_user'

def subscribed_receipts(args):
    return {
        'type': 'tx',
        'value': b'hash',
    }

def db_namespace():
    return 'pk'

def init(args, context, db):
    with open('./SaleClockAuction.abi', 'r') as f:
        sale_auction_abi = f.read()
    context['nonce'] = 1
    context['priv_key'] = PrivateKey(bytes(bytearray.fromhex(args['priv_key'])), raw=True)
    context['sale_auction'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['sale_auction_addr'])), abi=sale_auction_abi)

def run(args, context, db, receipts):
    logger = logging.getLogger('pk_user.run')
    [tx, _] = create_new_bid(context['sale_auction'], context['nonce'], db)
    if tx is None:
        return []
    logger.debug('new tx: %s', tx)

    tx = args['signer'](tx, context['priv_key'])
    context['nonce'] += 1
    return [tx]
