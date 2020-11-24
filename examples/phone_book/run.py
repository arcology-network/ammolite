import sys
sys.path.append('../../..')

import time
from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)

frontend = sys.argv[1]
account_file = sys.argv[2]
contract_address = sys.argv[3]

compiled_sol = compile_files(
    ['./contract/PhoneBook.sol', './contract/ConcurrentLibInterface.sol'],
    output_values = ['abi']
)
phone_book = compiled_sol['./contract/PhoneBook.sol:PhoneBook']

cli = Cli(HTTPProvider(frontend))
contract = cli.eth.contract(
    abi = phone_book['abi'],
    address = contract_address,
)

accounts = []
with open(account_file, 'r') as f:
    lines = f.readlines()
    for l in lines:
        parts = l.split(',')
        accounts.append(Account(parts[0]))

txs = {}
for acc in accounts:
    tx = contract.functions.set(12345678).buildTransaction({
        'gas': 1000000,
        'gasPrice': 1,
    })
    raw_tx, tx_hash = acc.sign(tx)
    txs[tx_hash] = raw_tx

print(txs)
while True:
    cli.sendTransactions(txs)
    time.sleep(10)
