from web3.auto import w3
from web3.logs import IGNORE
from secp256k1 import PrivateKey
import logging
from dapps.parallel_kitty.utils import find_event_logs_in_receipts

def name():
    return 'gen0_auction_creator'

def subscribed_receipts(args):
    return {
        'type': 'contract',
        'value': bytes(bytearray.fromhex(args['contract_address'])),
    }

def db_namespace():
    return 'pk'

def init(args, context, db):
    with open('./KittyCore.abi', 'r') as f:
        abi = f.read()
    context['nonce'] = 1
    context['priv_key'] = PrivateKey(bytes(bytearray.fromhex(args['priv_key'])), raw=True)
    context['contract'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['contract_address'])), abi=abi)

def run(args, context, db, receipts):
    logger = logging.getLogger('kitty_core.run')
    items = find_event_logs_in_receipts(
        args['logparser'],
        args['contract_address'],
        context['contract'].events.Birth(),
        receipts.values(),
        ['kittyId', 'matronId', 'sireId', 'genes']
    )
    for i in items:
        db.kitties.insert_one(i)
        logger.info('kitty(%s) inserted to kitties', i['kittyId'])

    tx = context['contract'].functions.createGen0Auction(context['nonce']).buildTransaction({
        'nonce': context['nonce'],
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    })
    tx['data'] = bytearray.fromhex(tx['data'][2:])

    tx = args['signer'](tx, context['priv_key'])
    context['nonce'] += 1
    return [tx]