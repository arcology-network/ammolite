import sys
sys.path.append('../../..')

from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)
from utils import wait_for_receipt

frontend = sys.argv[1]
private_key = sys.argv[2]

compiled_sol = compile_files(
    ['./contract/PhoneBook.sol', './contract/ConcurrentLibInterface.sol'],
    output_values = ['abi', 'bin']
)

phone_book = compiled_sol['./contract/PhoneBook.sol:PhoneBook']

cli = Cli(HTTPProvider(frontend))
phone_book_contract = cli.eth.contract(
    abi = phone_book['abi'],
    bytecode = phone_book['bin']
)

account = Account(private_key)
raw_tx, tx_hash = account.sign(phone_book_contract.constructor().buildTransaction({
    'nonce': 1,
    'gas': 1000000,
    'gasPrice': 1,
}))
cli.sendTransactions({tx_hash: raw_tx})
receipt = wait_for_receipt(cli, tx_hash)

print('Deployment complete, run this command to start the test:')
print('python3 run.py {} accounts.txt {}'.format(frontend, receipt['contractAddress']))
