### Install solc

```Shell
$ pip3 install py-solc-x
```

```Python
>>> import solcx
>>> solcx.get_installable_solc_versions()
[Version('0.7.3'), Version('0.7.2'), Version('0.7.1'), Version('0.7.0'), Version('0.6.12'), Version('0.6.11'), Version('0.6.10'), Version('0.6.9'), Version('0.6.8'), Version('0.6.7'), Version('0.6.6'), Version('0.6.5'), Version('0.6.4'), Version('0.6.3'), Version('0.6.2'), Version('0.6.1'), Version('0.6.0'), Version('0.5.17'), Version('0.5.16'), Version('0.5.15'), Version('0.5.14'), Version('0.5.13'), Version('0.5.12'), Version('0.5.11'), Version('0.5.10'), Version('0.5.9'), Version('0.5.8'), Version('0.5.7'), Version('0.5.6'), Version('0.5.5'), Version('0.5.4'), Version('0.5.3'), Version('0.5.2'), Version('0.5.1'), Version('0.5.0'), Version('0.4.26'), Version('0.4.25'), Version('0.4.24'), Version('0.4.23'), Version('0.4.22'), Version('0.4.21'), Version('0.4.20'), Version('0.4.19'), Version('0.4.18'), Version('0.4.17'), Version('0.4.16'), Version('0.4.15'), Version('0.4.14'), Version('0.4.13'), Version('0.4.12'), Version('0.4.11')]
>>> solcx.install_solc(version='0.5.0')
Version('0.5.0')
>>> solcx.get_solc_version()
Version('0.5.0')
```

### Compile solidity code

```Python
>>> source = '''
... pragma solidity ^0.5.0;
... contract Example {
...     uint256 value = 0;
...     constructor(uint256 n) public {
...         value = n;
...     }
...     function func1(uint256 n) public {
...         value = n;
...     }
... }'''
>>> from solcx import compile_source
>>> compiled_sol = compile_source(source)
>>> _, contract_interface = compiled_sol.popitem()
```

### Deploy contract

```Python
>>> from ammolite import (HTTPProvider, Cli, Account)
>>> cli = Cli(HTTPProvider('http://localhost:8080'))
>>> example_contract = cli.eth.contract(abi = contract_interface['abi'], bytecode = contract_interface['bin'])
>>> tx = example_contract.constructor(1).buildTransaction({
...     'nonce': 1,
...     'gas': 100000,
...     'gasPrice': 100,
... })
>>> account = Account("cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865")
>>> raw_tx, tx_hash = account.sign(tx)
>>> cli.sendTransactions({tx_hash: raw_tx})
```

### Query transaction result

```Python
>>> receipt = cli.getTransactionReceipt(tx_hash)
```

### Call contract

```Python
>>> example_contract.setAddress(receipt['contractAddress'])
>>> tx = example_contract.functions.func1(2).buildTransaction({
...     'nonce': 2,
...     'gas': 200000,
...     'gasPrice': 100,
... })
>>> raw_tx, tx_hash = account.sign(tx)
>>> cli.sendTransactions({tx_hash: raw_tx})
```

### Get balance

**Cli.getBalance(address, height = -1)**

* address - account address as a 40 characters hex string;
* height - default is -1, means the latest.

For example: 

```Python
>>> balance = cli.getBalance("1234567890123456789012345678901234567890")
>>> balanceOnHeight = cli.getBalance("1234567890123456789012345678901234567890", height = 100)
```

### Get block

**Cli.getBlock(height)**

* height - height of block, use -1 to get the latest block.

For example:

```Python
>>> latestBlock = cli.getBlock(-1)
>>> blockOnHeight = cli.getBlock(100)
```

### Get an element in a concurrent container

**Cli.getContainerAt(contractAddress, containerID, key, containerType, height = -1)**

* contractAddress - contract address the container belongs to as a 40 characters hex string;
* containerID - name of the container;
* key - key of the element;
* containerType - type of the container, can be 'map', 'array', or 'queue';
* height - default is -1, means the latest.

For example:

```Python
>>> elem = cli.getContainerAt('1234567890123456789012345678901234567890', 'arrayid', '1', 'array', height = 1)
```

### Examples

* [Phone Book](https://github.com/arcology-network/ammolite/tree/master/examples/phone_book)
* [Main Service](https://github.com/arcology-network/ammolite/tree/master/examples/main_service)
* [Parallel Kitties](https://github.com/arcology-network/ammolite/tree/master/examples/parallel_kitties)
