import sys
sys.path.append('../../..')

from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)
from utils import wait_for_receipts

frontend = sys.argv[1]
private_key = sys.argv[2]
address = sys.argv[3]

compiled_sol = compile_files(
    ['./contract/Defer.sol', './contract/ConcurrentLibInterface.sol'],
    output_values = ['abi'],
)
defer = compiled_sol['./contract/Defer.sol:Defer']

cli = Cli(HTTPProvider(frontend))
defer_contract = cli.eth.contract(
    abi = defer['abi'],
    address = address,
)

account = Account(private_key)
txs = {}
hashes = []

for i in range(100):
    tx = defer_contract.functions.increase(i).buildTransaction({
        'nonce': 1 + i,
        'gas': 1000000000,
        'gasPrice': 1,
    })
    raw_tx, tx_hash = account.sign(tx)
    txs[tx_hash] = raw_tx
    hashes.append(tx_hash)

cli.sendTransactions(txs)
receipts = wait_for_receipts(cli, hashes)
for receipt in receipts:
    if receipt['status'] != 1:
        print(receipt)
        exit(1)

raw_tx, tx_hash = account.sign(defer_contract.functions.getCounter().buildTransaction({
    'gas': 1000000000,
    'gasPrice': 1,
}))
cli.sendTransactions({tx_hash: raw_tx})
receipts = wait_for_receipts(cli, [tx_hash])
print(receipts)
events = defer_contract.processReceipt(receipts[0])
print(events)
