import logging
from web3.auto import w3
from dapps.parallel_kitty.utils import find_event_logs_in_receipts

def name():
    return 'kitty_ownership'

def subscribed_receipts(args):
    return {
        'type': 'contract',
        'value': bytes(bytearray.fromhex(args['kitty_core_addr']))
    }

def db_namespace():
    return 'pk'

def init(args, context, db):
    with open('./KittyCore.abi', 'r') as f:
        abi = f.read()
    context['kitty_core'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['kitty_core_addr'])), abi=abi)

def run(args, context, db, receipts):
    logger = logging.getLogger('kitty_ownership.run')
    items = find_event_logs_in_receipts(
        args['logparser'],
        args['kitty_core_addr'],
        context['kitty_core'].events.Transfer(),
        receipts.values(),
        ['to', 'tokenId']
    )
    logger.info('%d Transfer event found.', len(items))
    for i in items:
        db.ownership.update(
            {'tokenId': i['tokenId']},
            {'tokenId': i['tokenId'], 'owner': i['to'][2:]},
            upsert=True
        )
    return []