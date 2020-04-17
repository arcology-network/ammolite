import logging
from secp256k1 import PrivateKey
from web3.auto import w3
import random
from dapps.parallel_kitty.utils import create_new_bid

def process_receipt(receipt, method, args, context):
    logger = logging.getLogger('kitty_raiser.process_receipt')
    if receipt.status != 1:
        logger.warn('failed to run tx in %s method', method)
        return
    if method == 'bid':
        context['kitties'].append(args['tokenId'])
        if len(context['kitties']) >= 2:
            context['action'] = 'breed'
            logger.info('now we have 2 kitties, begin to breed...')
        return
    elif method == 'breed':
        # If breed succeed, we wait for the birth of new kitty.
        context['action'] = 'wait'
        return
    else:
        logger.warn('unexpected method %s', method)

def gen_two_diff_rand(begin, end):
    while True:
        a = random.randint(begin, end)
        b = random.randint(begin, end)
        if a != b:
            return [a, b]

# Standard interfaces.

def name():
    return 'kitty_raiser'

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
    context['pending_txs'] = {}
    context['nonce'] = 1
    context['priv_key'] = PrivateKey(bytes(bytearray.fromhex(args['priv_key'])), raw=True)
    context['address'] = args['address'].lower()
    context['kitties'] = []
    context['action'] = 'prepare'

def run(args, context, db, receipts):
    logger = logging.getLogger('kitty_raiser.run')
    # Process receipts first.
    if len(context['pending_txs']) > 0:
        for hash in list(context['pending_txs']):
            if hash in receipts:
                tx = context['pending_txs'][hash]
                process_receipt(receipts[hash], tx['method'], tx['args'], context)
                del context['pending_txs'][hash]
    
    if context['action'] == 'prepare':
        [tx, tokenId] = create_new_bid(context['sale_auction'], context['nonce'], db)
        if tx is None:
            return []
        tx = args['signer'](tx, context['priv_key'])
        context['nonce'] += 1
        context['pending_txs'][tx['hash']] = {
            'method': 'bid',
            'args': {
                'tokenId': tokenId,
            },
        }
        return [tx]
    elif context['action'] == 'breed':
        # Randomly select two cats to breed.
        # total = len(context['kitties'])
        # [a, b] = gen_two_diff_rand(0, total - 1)
        [a, b] = [0, 1]
        tx = context['kitty_core'].functions.breedWithAuto(
            int(context['kitties'][a], base=16),
            int(context['kitties'][b], base=16)
        ).buildTransaction({
            'value': int(1e15),
            'nonce': context['nonce'],
            'gas': 1000000,
            'gasPrice': 1,
            'chainId': 1,
        })
        tx['data'] = bytearray.fromhex(tx['data'][2:])
        tx = args['signer'](tx, context['priv_key'])
        context['nonce'] += 1
        context['pending_txs'][tx['hash']] = {
            'method': 'breed',
            'args': None,
        }
        context['pregnantMatronId'] = context['kitties'][a]
        return [tx]
    elif context['action'] == 'wait':
        # Check if the new baby is born.
        items = db.newborns.find({
            'matronId': context['pregnantMatronId'],
        })
        for i in items:
            context['kitties'].append(i['kittyId'])
            db.newborns.delete_one({
                'matronId': context['pregnantMatronId']
            })
            logger.info('new kitty is born, start another breed...')
            context['action'] = 'breed'
        return []
    else:
        logger.warn('unexpected action %s', context['action'])
        return []
            