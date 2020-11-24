import sys
sys.path.append('../../..')

from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)
from utils import wait_for_receipt

# frontend = 'http://localhost:8080'
# private_key = 'cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865'
frontend = sys.argv[1]
private_key = sys.argv[2]

compiled_sol = compile_files(
    ['./contract/MainService.sol', './contract/ConcurrentLibInterface.sol'],
    output_values = ['abi', 'bin']
)

storage_svc = compiled_sol['./contract/MainService.sol:StorageService']
computing_svc = compiled_sol['./contract/MainService.sol:ComputingService']
main_svc = compiled_sol['./contract/MainService.sol:MainService']

cli = Cli(HTTPProvider(frontend))
storage_svc_contract = cli.eth.contract(
    abi = storage_svc['abi'],
    bytecode = storage_svc['bin']
)
computing_svc_contract = cli.eth.contract(
    abi = computing_svc['abi'],
    bytecode = computing_svc['bin']
)
main_svc_contract = cli.eth.contract(
    abi = main_svc['abi'],
    bytecode = main_svc['bin']
)

account = Account(private_key)
tx1, hash1 = account.sign(storage_svc_contract.constructor().buildTransaction({
    'nonce': 1,
    'gas': 1000000,
    'gasPrice': 1,
}))
tx2, hash2 = account.sign(computing_svc_contract.constructor().buildTransaction({
    'nonce': 2,
    'gas': 1000000,
    'gasPrice': 1,
}))
tx3, hash3 = account.sign(main_svc_contract.constructor().buildTransaction({
    'nonce': 3,
    'gas': 1000000,
    'gasPrice': 1,
}))

cli.sendTransactions({hash1: tx1, hash2: tx2, hash3: tx3})
receipt1 = wait_for_receipt(cli, hash1)
receipt2 = wait_for_receipt(cli, hash2)
receipt3 = wait_for_receipt(cli, hash3)

print('Deployment complete, run this command to start the test:')
print('python3 run.py {} {} {} {} {}'.format(frontend, private_key, receipt1['contractAddress'], receipt2['contractAddress'], receipt3['contractAddress']))
