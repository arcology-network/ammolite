import logging

from web3.auto import w3
from secp256k1 import PrivateKey
from dapps.parallel_kitty.utils import create_new_bid



def name():
    return 'siring_auction_creator'

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
    context['sale_auction'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['sale_auction_addr'])), abi=sale_auction_abi)
    with open('./KittyCore.abi', 'r') as f:
        kitty_core_abi = f.read()
    context['kitty_core'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['kitty_core_addr'])), abi=kitty_core_abi)
    context['nonce'] = 1
    context['priv_key'] = PrivateKey(bytes(bytearray.fromhex(args['priv_key'])), raw=True)
    context['kitty'] = None
    context['action'] = 'prepare'
    context['last_tx'] = None

def run(args, context, db, receipts):
    logger = logging.getLogger('siring_auction_creator.run')
    # Process receipts first.
    if context['last_tx'] != None and context['last_tx']['hash'] in receipts:
        if receipts[context['last_tx']['hash']].status != 1:
            logger.warn('failed to run last tx: %s', context['last_tx']['method'])
            context['last_tx'] = None
            return []
        if context['last_tx']['method'] == 'bid':
            context['kitty'] = context['last_tx']['tokenId']
            context['action'] = 'ready'
            logger.info('ready to create siring auction...')
        elif context['last_tx']['method'] == 'createSiringAuction':
            context['action'] = 'wait_for_bid'
        else:
            logger.warn('unsupported method %s', context['last_tx']['method'])
        context['last_tx'] = None
    # Finite state machine.
    if context['action'] == 'prepare':
        [tx, tokenId] = create_new_bid(context['sale_auction'], context['nonce'], db)
        if tx is None:
            return []
        tx = args['signer'](tx, context['priv_key'])
        context['nonce'] += 1
        context['last_tx'] = {
            'hash': tx['hash'],
            'method': 'bid',
            'tokenId': tokenId,
        }
        logger.info('bid for gen 0 kitty: %s', tokenId)
        return [tx]
    elif context['action'] == 'ready':
        tx = context['kitty_core'].functions.createSiringAuction(
            int(context['kitty'], base=16),
            int(1e15),
            0,
            60 # Duration must greater than or equal to 1 minute.
        ).buildTransaction({
            'nonce': context['nonce'],
            'gas': 1000000,
            'gasPrice': 1,
            'chainId': 1,
        })
        tx['data'] = bytearray.fromhex(tx['data'][2:])
        tx = args['signer'](tx, context['priv_key'])
        context['nonce'] += 1
        context['last_tx'] = {
            'hash': tx['hash'],
            'method': 'createSiringAuction',
        }
        return [tx]
    elif context['action'] == 'wait_for_bid':
        items = db.siringauctioncomplete.find({
            'sireId': context['kitty']
        })
        for i in items:
            db.siringauctioncomplete.delete_one({
                'sireId': i['sireId']
            })
            logger.info('new kitty is born, start another siring auction...')
            context['action'] = 'ready'
            return []
        logger.info('wait_for_bid......')
        return []
    else:
        logger.warn('unsupported action: %s', context['action'])
        return []

            


