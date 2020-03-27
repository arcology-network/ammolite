import logging
import time

def runDAppContainer(instances, input, output, quit):
    logger = logging.getLogger('runDAppContainer')
    while not quit.is_set(): # or not input.empty():
        logger.debug('enter')
        try:
            receipts = input.get(timeout=1)
        except:
            logger.debug('get new receipts timeout')
            continue
        start = time.time_ns()
        logger.debug('Received %d receipts', len(receipts))
        txs = {}
        for i in range(len(instances)):
            # TODO: add receipts filter for contract subscriber.
            if instances[i] == None:
                continue
            try:
                result = instances[i].run(receipts)
            except Exception as e:
                logger.warn(e)
                instances[i] = None
            else:
                logger.debug('dappinstance.run return')
                logger.debug('dappinstance %s returns %d txs', result[0], len(result[1]))
                if len(result[1]) != 0:
                    if result[0] in txs:
                        txs[result[0]] = txs[result[0]] + result[1]
                    else:
                        txs[result[0]] = result[1]
        output.put(txs)
        logger.debug('finish in %d ns', (time.time_ns() - start))
    logger.debug('exit')