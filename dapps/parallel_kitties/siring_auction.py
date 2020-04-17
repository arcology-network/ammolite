import logging
from web3.auto import w3
from dapps.parallel_kitty.utils import find_event_logs_in_receipts

def name():
    return 'siring_auction'

def subscribed_receipts(args):
    return {
        'type': 'contract',
        'value': bytes(bytearray.fromhex(args['siring_auction_addr']))
    }

def db_namespace():
    return 'pk'

def init(args, context, db):
    with open('./SiringClockAuction.abi', 'r') as f:
        abi = f.read()
    context['siring_auction'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['siring_auction_addr'])), abi=abi)

def run(args, context, db, receipts):
    logger = logging.getLogger('siring_auction.run')
    items = find_event_logs_in_receipts(
        args['logparser'],
        args['siring_auction_addr'],
        context['siring_auction'].events.AuctionSuccessful(),
        receipts.values(),
        ['tokenId']
    )
    for i in items:
        x = db.siringauction.delete_one({'tokenId': i['tokenId']})
        if x.deleted_count != 1:
            logger.warn('failed to delete token(%s) from siringauction', i['tokenId'])
            continue
        logger.info('token(%s) deleted from siringauction', i['tokenId'])
    
    items = find_event_logs_in_receipts(
        args['logparser'],
        args['siring_auction_addr'],
        context['siring_auction'].events.AuctionCreated(),
        receipts.values(),
        ['tokenId', 'startingPrice', 'endingPrice', 'duration']
    )
    for i in items:
        x = db.siringauction.insert_one(i)
        logger.info('token(%s) inserted to siringauction', i['tokenId'])
    return []