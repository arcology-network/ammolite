import sys
sys.path.append('../')

from solcx import compile_source
from ammolite import (Cli, HTTPProvider, Account)

source = '''
pragma solidity ^0.5.0;

contract Example {
    uint256 value = 0;

    constructor(uint256 n) public {
        value = n;
    }

    function func1(uint256 n) public {
        value = n;
    }
}
'''
compiled_sol = compile_source(source)

_, contract_interface = compiled_sol.popitem()
cli = Cli(HTTPProvider("http://localhost:8080"))

example_contract = cli.eth.contract(abi = contract_interface['abi'], bytecode = contract_interface['bin'])
tx = example_contract.constructor(1).buildTransaction({
    'nonce': 1,
    'gas': 100000,
    'gasPrice': 100,
})
print(tx)

account = Account("cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865")
raw_tx, tx_hash = account.sign(tx)
# print("raw_tx = {}, tx_hash = {}".format(raw_tx, tx_hash))

cli.sendTransactions({tx_hash: raw_tx})
receipt = cli.getTransactionReceipt(tx_hash)
example_contract.setAddress(receipt['contractAddress'])
tx = example_contract.functions.func1(2).buildTransaction({
    'nonce': 2,
    'gas': 200000,
    'gasPrice': 100,
})
raw_tx, tx_hash = account.sign(tx)
cli.sendTransactions({tx_hash: raw_tx})

balance = cli.getBalance("1234567890123456789012345678901234567890", height = 1)
print('balance = {}'.format(balance))

receipt = cli.getTransactionReceipt("1234567890123456789012345678901234567890")
print('receipt = {}'.format(receipt))

block = cli.getBlock(123)
print('block = {}'.format(block))

elem = cli.getContainerAt('1234567890123456789012345678901234567890', 'cid', '1', 'array', height = 1)
print('elem = {}'.format(elem))