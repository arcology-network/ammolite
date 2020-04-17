from web3.auto import w3 
from eth_signer import sign_transaction
from secp256k1 import PrivateKey
import grpc
import clientsvc_pb2_grpc
import clientsvc_pb2

ceo_priv_key = PrivateKey(bytes(bytearray.fromhex('cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865')))
coo_priv_key = PrivateKey(bytes(bytearray.fromhex('3d8db4982173aad36b0c10c91a0f94b1685f773bc7d865d445426b9a6676cd40')))
cfo_priv_key = PrivateKey(bytes(bytearray.fromhex('42e30ad7f9b7ccb4c19d14277c76c15fddc461548be3102dcb4bbfd7b602c07a')))
kitty_core_addr = '422837ded18e01b60e03c47d628637a0e9fb412e'
sale_auction_addr = '796b69363d0d6b8c34e80fb8fff186c43ec79606'
siring_auction_addr = '30a977d84d7214d4ecd04f4a61e167f9966535c0'
gene_science_addr = 'a2da9525bb3a09cec0716e47ab6d3e1734b6b035'
ceo_addr = '585b43a21347782848338F9b74B12eA8C77fF1D6'
coo_addr = '5c6dC6Df50C98C482BCBF3b617a0392B580862A6'
cfo_addr = '18317215dF750ebA81C3cfa11c6711f02da1bfc4'

def sendTxs(txs, priv_key, stub):
    list = []
    for tx in txs:
        tx['data'] = bytearray.fromhex(tx['data'][2:])
        tx = sign_transaction(tx, priv_key)
        list.append(clientsvc_pb2.NewTransactionsRequest.Transaction(
            raw_transaction = tx['raw'],
            hash = tx['hash'],
            to = tx['to'],
        ))
    transactions = {}
    transactions['parallel_kitty'] = clientsvc_pb2.NewTransactionsRequest.Transactions(
        list = list,
    )

    request = clientsvc_pb2.NewTransactionsRequest(
        client = 'pk_setup',
        transactions = transactions,
    )
    response = stub.NewTransactions(request, timeout=3)
    print(response.status)

with open('./KittyCore.abi', 'r') as f:
    abiStr = f.read()
    kittyCore = w3.eth.contract(address=bytes(bytearray.fromhex(kitty_core_addr)), abi=abiStr)

with grpc.insecure_channel('localhost:50000') as channel:
    stub = clientsvc_pb2_grpc.ClientServiceStub(channel)
    txs = []
    txs.append(kittyCore.functions.setSaleAuctionAddress(bytes(bytearray.fromhex(sale_auction_addr))).buildTransaction({
        'nonce': 1,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    }))
    txs.append(kittyCore.functions.setSiringAuctionAddress(bytes(bytearray.fromhex(siring_auction_addr))).buildTransaction({
        'nonce': 2,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    }))
    txs.append(kittyCore.functions.setGeneScienceAddress(bytes(bytearray.fromhex(gene_science_addr))).buildTransaction({
        'nonce': 3,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    }))
    txs.append(kittyCore.functions.setCOO(bytes(bytearray.fromhex(coo_addr))).buildTransaction({
        'nonce': 4,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    }))
    txs.append(kittyCore.functions.setCFO(bytes(bytearray.fromhex(cfo_addr))).buildTransaction({
        'nonce': 5,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    }))
    txs.append(kittyCore.functions.unpause().buildTransaction({
        'nonce': 6,
        'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
    }))

    sendTxs(txs, ceo_priv_key, stub)


