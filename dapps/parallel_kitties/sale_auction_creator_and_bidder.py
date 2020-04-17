import logging
from web3.auto import w3
from secp256k1 import PrivateKey
from dapps.parallel_kitty.utils import create_new_bid

def name():
    return 'sale_auction_creator_and_bidder'

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
    context['role'] = 'bidder'
    context['last_tx'] = None

def run(args, context, db, receipts):
    logger = logging.getLogger('sale_auction_creator_and_bidder.run')

    if context['last_tx'] != None and context['last_tx']['hash'] in receipts:
        if receipts[context['last_tx']['hash']].status != 1:
            logger.warn('failed to run last tx: %s', context['last_tx']['method'])
            context['last_tx'] = None
            return []
        if context['last_tx']['method'] == 'bid':
            context['kitty'] = context['last_tx']['tokenId']
            context['role'] = 'creator'
            logger.info('ready to create sale auction...')
        elif context['last_tx']['method'] == 'createSaleAuction':
            context['role'] = 'bidder'
            logger.info('ready to bid a new kitty...')
        else:
            logger.warn('unsupported method %s', context['last_tx']['method'])
        context['last_tx'] = None

    if context['role'] == 'bidder':
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
        logger.info('bid for kitty: %s', tokenId)
        return [tx]
    elif context['role'] == 'creator':
        tx = context['kitty_core'].functions.createSaleAuction(
            int(context['kitty'], base=16),
            int(1e15),
            0,
            60
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
            'method': 'createSaleAuction',
        }
        return [tx]
    else:
        logger.warn('unsupported role: %s', context['role'])
        return []