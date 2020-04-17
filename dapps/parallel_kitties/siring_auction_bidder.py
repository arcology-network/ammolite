import logging
from web3.auto import w3
from secp256k1 import PrivateKey
from dapps.parallel_kitty.utils import create_new_bid, create_new_bid_on_siring_auction

def name():
    return 'siring_auction_bidder'

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
    logger = logging.getLogger('siring_auction_bidder')
    # Process receipts first.
    if context['last_tx'] != None and context['last_tx']['hash'] in receipts:
        if receipts[context['last_tx']['hash']].status != 1:
            logger.warn('failed to run last tx: %s', context['last_tx']['method'])
            context['last_tx'] = None
            return []
        if context['last_tx']['method'] == 'bid':
            context['kitty'] = context['last_tx']['tokenId']
            context['action'] = 'ready'
            logger.info('ready to bid on siring auction...')
        elif context['last_tx']['method'] == 'bidOnSiringAuction':
            context['action'] = 'wait_for_give_birth'
        else:
            logger.warn('unsupported method %s', context['last_tx']['method'])
        context['last_tx'] = None
    # Finite state machine
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
        [tx, tokenId] = create_new_bid_on_siring_auction(context['kitty_core'], context['nonce'], context['kitty'], db)
        if tx is None:
            return []
        tx = args['signer'](tx, context['priv_key'])
        context['nonce'] += 1
        context['last_tx'] = {
            'hash': tx['hash'],
            'method': 'bidOnSiringAuction',
        }
        logger.info('bid on siring auction: %s', tokenId)
        return [tx]
    elif context['action'] == 'wait_for_give_birth':
        # Check if the new baby is born.
        items = db.newborns.find({
            'matronId': context['kitty']
        })
        for i in items:
            db.newborns.delete_one({
                'kittyId': i['kittyId']
            })
            logger.info('new kitty is born, start another bid...')
            context['action'] = 'ready'
            db.siringauctioncomplete.insert_one({
                'sireId': i['sireId']
            })
            return []
        logger.info('wait_for_give_birth...')
        return []
    else:
        logger.warn('unsupported action: %s', context['action'])
        return []