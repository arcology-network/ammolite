import grpc
import sys

from secp256k1 import PrivateKey
from yaml import load, Loader

import rlp
import sha3

import clientsvc_pb2
import clientsvc_pb2_grpc
import eth_signer

with open(sys.argv[1], 'r') as cf:
    config = load(cf, Loader=Loader)

priv_key = PrivateKey(bytes(bytearray.fromhex(config['priv_key'])))
code = bytes(bytearray.fromhex(config['code']))
data = code
if 'params' in config:
    for param in config['params']:
        pStr = '0' * (64 - len(param)) + param
        pbytes = bytes(bytearray.fromhex(pStr))
        print(pStr)
        data += pbytes

with grpc.insecure_channel(config['client_svc']) as channel:
    stub = clientsvc_pb2_grpc.ClientServiceStub(channel)
    tx = {
        'to': b'',
        'value': 0,
        'gas': int(1e10),
        'gasPrice': 1,
        'nonce': 0,
        'data': data,
        'v': 1,
        'r': 0,
        's': 0,
    }
    tx = eth_signer.sign_transaction(tx, priv_key)
    tx['to'] = bytes(bytearray.fromhex(config['address']))

    list = []
    list.append(clientsvc_pb2.NewTransactionsRequest.Transaction(
        raw_transaction = tx['raw'],
        hash = tx['hash'],
        to = tx['to'],
    ))

    transactions = {}
    transactions[config['dapp']] = clientsvc_pb2.NewTransactionsRequest.Transactions(
        list = list,
    )

    request = clientsvc_pb2.NewTransactionsRequest(
        client = 'deployer',
        transactions = transactions,
    )
    response = stub.NewTransactions(request, timeout=3)
    print(response.status)

    sender = bytes.fromhex(config['address'])
    nonce = 0
    contract_address = sha3.keccak_256(rlp.encode([sender, nonce])).hexdigest()[-40:]
    print(contract_address)
