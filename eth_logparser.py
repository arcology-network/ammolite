import logging
from web3.logs import IGNORE

def parse_log(event, receipt):
    logger = logging.getLogger('parse_log')
    logs = []
    for log in receipt.logs:
        logs.append({
            'data': log.data,
            'topics': log.topics,
            'logIndex': 0,
            'transactionIndex': 0,
            'transactionHash': b'',
            'address': log.address,
            'blockHash': b'',
            'blockNumber': 1,
        })
    txReceipt = {
        'status': receipt.status,
        'contractAddress': receipt.contract_address,
        'logs': logs,
    }
    logger.debug('txReceipt: %s', str(txReceipt))
    processed_receipt = event.processReceipt(txReceipt, errors=IGNORE)
    logger.debug('processed_receipt: %s', str(processed_receipt))

    ret = []
    for r in processed_receipt:
        ret.append({
            'args': r['args'],
            'event': r['event'],
            'address': r['address'],
        })
    return ret
