import time


def wait_for_receipts(cli, hashes):
    # print(hashes)
    receipts = {}
    retry_time = 0
    while True:
        rs = cli.getTransactionReceipts(hashes)
        if rs is None or len(rs) == 0:
            continue
        if len(rs) != len(hashes):
            time.sleep(1)
            retry_time += 1
            if retry_time > 120:
                print('expected = {}, got = {}'.format(len(hashes), len(rs)))
                print('-----------------------------------------------------------------------------------', file=sys.stderr)
                for h in hashes:
                    print(h.hex(), file=sys.stderr)
                exit(1)
            continue
        remains = []
        for i in range(len(rs)):
            # print(rs[i])
            # print(hashes[i])
            if rs[i] is not None:
                receipts[hashes[i]] = rs[i]
            else:
                remains.append(hashes[i])
        if len(remains) == 0:
            return receipts
        
        time.sleep(3)
        hashes = remains


def wait_for_receipt(cli, tx_hash):
    while True:
        receipts = cli.getTransactionReceipts([tx_hash])
        print(receipts)
        if receipts is not None and len(receipts) == 1:
            return receipts[0]
        time.sleep(3)
