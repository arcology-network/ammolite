import logging
import time
import traceback, sys

def runDAppContainer(blockinfo, instances, input, output, quit):
    logger = logging.getLogger('runDAppContainer')
    block_no = blockinfo['block_no']
    while not quit.is_set(): # or not input.empty():
        logger.debug('enter')
        block_info = {
            'block_no': block_no,
            'timestamp': block_no * blockinfo['seconds_per_block'],
        }
        try:
            receipts = input.get(timeout=1)
        except:
            logger.debug('get new receipts timeout')
            continue
        start = time.time_ns()
        logger.info('Received %d receipts', len(receipts))
        txs = {}
        logger.info('block_info = %s', block_info)
        for i in range(len(instances)):
            # TODO: add receipts filter for contract subscriber.
            if instances[i] == None:
                continue
            try:
                result = instances[i].run(block_info, receipts)
            except Exception as e:
                logger.warn('%s: %s', instances[i].dapp.name(), e)
                traceback.print_exc(file=sys.stdout)
                instances[i] = None
            else:
                logger.debug('dappinstance.run return')
                logger.info('dappinstance %s returns %d txs', result[0], len(result[1]))
                if len(result[1]) != 0:
                    if result[0] in txs:
                        txs[result[0]] = txs[result[0]] + result[1]
                    else:
                        txs[result[0]] = result[1]
        output.put(txs)
        block_no += 1
        logger.debug('finish in %d ns', (time.time_ns() - start))
    logger.debug('exit')