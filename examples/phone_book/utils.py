import time

def wait_for_receipt(cli, tx_hash):
    while True:
        receipt = cli.getTransactionReceipt(tx_hash)
        if receipt is not None:
            return receipt
        time.sleep(3)