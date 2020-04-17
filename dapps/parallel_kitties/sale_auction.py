from web3.auto import w3
import logging
from dapps.parallel_kitty.utils import find_event_logs_in_receipts

def name():
    return 'sale_auction'

def subscribed_receipts(args):
    return {
        'type': 'contract',
        'value': bytes(bytearray.fromhex(args['contract_address'])),
    }

def db_namespace():
    return 'pk'

def init(args, context, db):
    with open('./SaleClockAuction.abi', 'r') as f:
        abi = f.read()
    context['contract'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['contract_address'])), abi=abi)

def run(args, context, db, receipts):
    logger = logging.getLogger('sale_auction.run')
    items = find_event_logs_in_receipts(
        args['logparser'],
        args['contract_address'],
        context['contract'].events.AuctionSuccessful(),
        receipts.values(),
        ['tokenId']
    )
    for i in items:
        x = db.saleauction.delete_one({'tokenId': i['tokenId']})
        if x.deleted_count != 1:
            logger.warn('failed to delete token(%s) from saleauction', i['tokenId'])
            continue
        logger.info('token(%s) deleted from saleauction', i['tokenId'])
    
    items = find_event_logs_in_receipts(
        args['logparser'],
        args['contract_address'],
        context['contract'].events.AuctionCreated(),
        receipts.values(),
        ['tokenId', 'startingPrice', 'endingPrice', 'duration']
    )
    for i in items:
        x = db.saleauction.insert_one(i)
        logger.info('token(%s) inserted to saleauction', i['tokenId'])
    return []