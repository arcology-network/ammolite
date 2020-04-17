import logging
from secp256k1 import PrivateKey
from web3.auto import w3
from dapps.parallel_kitty.utils import find_event_logs_in_receipts

def name():
    return 'kitty_miner'

def subscribed_receipts(args):
    return {
        'type': 'contract',
        'value': bytes(bytearray.fromhex(args['kitty_core_addr'])),
    }

def db_namespace():
    return 'pk'

def init(args, context, db):
    with open('./KittyCore.abi', 'r') as f:
        kitty_core_abi = f.read()
    context['kitty_core'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['kitty_core_addr'])), abi=kitty_core_abi)
    context['pending_txs'] = {}
    context['nonce'] = 1
    context['priv_key'] = PrivateKey(bytes(bytearray.fromhex(args['priv_key'])), raw=True)
    context['pregnant_kitties'] = {}

def run(args, context, db, receipts):
    logger = logging.getLogger('kitty_miner.run')
    if len(context['pending_txs']) > 0:
        for hash in list(context['pending_txs']):
            if hash in receipts:
                items = find_event_logs_in_receipts(
                    args['logparser'],
                    args['kitty_core_addr'],
                    context['kitty_core'].events.Birth(),
                    [receipts[hash]],
                    ['kittyId', 'matronId', 'sireId', 'genes']
                )
                for i in items:
                    db.newborns.insert_one(i)
                    logger.info('newborn kitty: %s', i)
                del context['pending_txs'][hash]
    
    # logger.info('receipts: %s', receipts)
    items = find_event_logs_in_receipts(
        args['logparser'],
        args['kitty_core_addr'],
        context['kitty_core'].events.AutoBirth(),
        receipts.values(),
        ['matronId', 'cooldownEndTime']
    )
    for i in items:
        logger.info('auto birth event: %s', i)
        context['pregnant_kitties'][i['matronId']] = int(i['cooldownEndTime'], base=16)
    logger.info('pregnant kitties: %s', context['pregnant_kitties'])

    tx_list = []
    for matronId in list(context['pregnant_kitties']):
        if context['timestamp'] >= context['pregnant_kitties'][matronId]:
            tx = context['kitty_core'].functions.giveBirth(int(matronId, base=16)).buildTransaction({
                'nonce': context['nonce'],
                'gas': 1000000,
                'gasPrice': 1,
                'chainId': 1,
            })
            tx['data'] = bytearray.fromhex(tx['data'][2:])
            tx = args['signer'](tx, context['priv_key'])
            context['nonce'] += 1
            context['pending_txs'][tx['hash']] = {}
            tx_list.append(tx)
            del context['pregnant_kitties'][matronId]
    return tx_list