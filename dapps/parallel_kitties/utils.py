import logging



def find_event_logs_in_receipts(parser, contract_addr, event, receipts, keys):
    logger = logging.getLogger('utils.find_event_logs_in_receipts')
    items = []
    for r in receipts:
        if r.status != 1:
            logger.debug('!!!failed to run tx!!!')
            continue
        
        found = False
        for log in r.logs:
            if log.address == bytes(bytearray.fromhex(contract_addr)):
                found = True
                break
        if not found:
            continue

        processed_logs = parser(event, r)
        for pl in processed_logs:
            if 'event' not in pl:
                continue
            item = {}
            for k in keys:
                if type(pl['args'][k]) == str:
                    item[k] = pl['args'][k]
                else:
                    item[k] = pl['args'][k].to_bytes(32, byteorder='big').hex()
            items.append(item)
    return items

def create_new_bid(contract, nonce, db):
    items = db.saleauction.aggregate([{'$sample': {'size': 1}}])
    kitty_to_bid = None
    for i in items:
        kitty_to_bid = i
        break
    if kitty_to_bid is None:
        return [None, None]
    tx = contract.functions.bid(int(kitty_to_bid['tokenId'], base=16)).buildTransaction({
        'value': int(kitty_to_bid['startingPrice'], base=16),
        'nonce': nonce,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    })
    tx['data'] = bytearray.fromhex(tx['data'][2:])
    return [tx, kitty_to_bid['tokenId']]

def create_new_bid_on_siring_auction(contract, nonce, matron_id, db):
    items = db.siringauction.aggregate([{'$sample': {'size': 1}}])
    kitty_to_bid = None
    for i in items:
        kitty_to_bid = i
        break
    if kitty_to_bid is None:
        return [None, None]
    tx = contract.functions.bidOnSiringAuction(int(kitty_to_bid['tokenId'], base=16), int(matron_id, base=16)).buildTransaction({
        'value': int(1e15 * 2),
        'nonce': nonce,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    })
    tx['data'] = bytearray.fromhex(tx['data'][2:])
    return [tx, kitty_to_bid['tokenId']]