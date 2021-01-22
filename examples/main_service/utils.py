import time

def wait_for_receipts(cli, hashes):
    # print(hashes)
    receipts = {}
    while True:
        rs = cli.getTransactionReceipts(hashes)
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
        if len(receipts) == 1:
            return receipts[0]
        time.sleep(3)
