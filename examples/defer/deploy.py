import sys
sys.path.append('../../..')

from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)
from utils import wait_for_receipt

frontend = sys.argv[1]
private_key = sys.argv[2]

compiled_sol = compile_files(
    ['./contract/Defer.sol', './contract/ConcurrentLibInterface.sol'],
    output_values = ['abi', 'bin'],
)

defer = compiled_sol['./contract/Defer.sol:Defer']
cli = Cli(HTTPProvider(frontend))
defer_contract = cli.eth.contract(
    abi = defer['abi'],
    bytecode = defer['bin'],
)

account = Account(private_key)
raw_tx, tx_hash = account.sign(defer_contract.constructor().buildTransaction({
    'nonce': 1,
    'gas': 1000000000,
    'gasPrice': 1,
}))
cli.sendTransactions({tx_hash: raw_tx})
receipt = wait_for_receipt(cli, tx_hash)
print(f'python test.py {frontend} {private_key} {receipt["contractAddress"]}')