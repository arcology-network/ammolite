import sys
sys.path.append('../../..')

import time
from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)

frontend = sys.argv[1]
private_key = sys.argv[2]
storage_svc_address = sys.argv[3]
computing_svc_address = sys.argv[4]
main_svc_address = sys.argv[5]

compiled_sol = compile_files(
    ['./contract/MainService.sol', './contract/ConcurrentLibInterface.sol'],
    output_values = ['abi'])
main_svc = compiled_sol['./contract/MainService.sol:MainService']

cli = Cli(HTTPProvider(frontend))
main_service_contract = cli.eth.contract(
    abi = main_svc['abi'],
    address = main_svc_address,
)

account = Account(private_key)
buf_size = 10
batch_size = 2
index = 0
buf = []

def create_new_txs(offset):
    txs = []
    for i in range(batch_size):
        tx = main_service_contract.functions.func(
            offset+i,
            int(0x010203040506),
            b'This is the data segment',
            storage_svc_address,
            int(0x010203),
            computing_svc_address,
            5
        ).buildTransaction({
            'nonce': offset+i,
            'gas': 1000000,
            'gasPrice': 1,
            'value': 10,
        })
        raw_tx, tx_hash = account.sign(tx)
        txs.append([tx_hash, raw_tx])
    return txs

while True:
    if len(buf) < buf_size:
        txs = create_new_txs(len(buf))
        buf.extend(txs)
    else:
        if index + batch_size >= buf_size:
            index = 0
    txs = buf[index:index+batch_size]
    index += batch_size

    transactions = {}
    for tx in txs:
        transactions[tx[0]] = tx[1]
    cli.sendTransactions(transactions)
    time.sleep(10)