from concurrent import futures
import grpc
import queue
import threading
import logging
import time
import os
import signal
import sys

from pymongo import MongoClient
from yaml import load, Loader

import dappcontainer_pb2
import dappcontainer_pb2_grpc
from dappcontainer import runDAppContainer
from dappinstance import DAppInstance
from eth_signer import sign_transaction as eth_sign_transaction
from eth_logparser import parse_log
import clientsvc_pb2
import clientsvc_pb2_grpc

startTime = 0

class DAppContainer(dappcontainer_pb2_grpc.DAppContainerServicer):
    def __init__(self, queue):
        self.queue = queue

    def NewReceipts(self, request_iterator, context):
        global startTime
        receipts = {}
        for r in request_iterator:
            receipts[r.txhash] = r
        startTime = time.time_ns()
        self.queue.put(receipts)
        return dappcontainer_pb2.NewReceiptsResponse(status=0)

def receiveNewTxs(connstr, client_service, queue, quit):
    logger = logging.getLogger('receiveNewTxs')
    while not quit.isSet() or not queue.empty():
        logger.debug('enter')
        try:
            result = queue.get(timeout=1)
        except:
            logger.debug('get new txs timeout')
            continue
        count = 0
        transactions = {}
        for dappName in result.keys():
            count += len(result[dappName])
            list = []
            for tx in result[dappName]:
                list.append(clientsvc_pb2.NewTransactionsRequest.Transaction(
                    raw_transaction = tx['raw'],
                    hash = tx['hash'],
                    to = tx['to'],
                ))
            transactions[dappName] = clientsvc_pb2.NewTransactionsRequest.Transactions(
                list = list,
            )
        logger.info('generate %d txs in %d ns', count, (time.time_ns() - startTime))
        request = clientsvc_pb2.NewTransactionsRequest(
            client = connstr,
            transactions = transactions,
        )
        logger.debug('before NewTransactions')
        response = client_service.NewTransactions(request, timeout=3)
        logger.debug('NewTransaction response status %d', response.status)
    logger.debug('consumer exit')
    response = client_service.UnregisterClient(clientsvc_pb2.UnregisterClientRequest(
        address = connstr,   
    ))
    logger.debug('UnregisterClient response status %d', response.status)

def register_client(connstr, stub, subs):
    sub_infos = {}
    for dappName in subs.keys():
        sub_infos[dappName] = clientsvc_pb2.NewClientRequest.SubInfo(
            type = subs[dappName]['type'],
            value = subs[dappName]['value'],
        )
    response = stub.RegisterNewClient(clientsvc_pb2.NewClientRequest(
        address = connstr,
        sub_infos = sub_infos,
    ), timeout=3)
    return response

server = None
quit = None

def sighandler(sig, frame):
    global server
    global quit
    quit.set()
    logging.getLogger('sighandler').info('Ctrl-C pressed')
    time.sleep(3)
    server.stop(None)
    sys.exit(0)

def serve(config, accounts):
    logging.basicConfig(format = '%(asctime)s [%(levelname)s]: [%(name)s] %(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')
    logger = logging.getLogger('serve')

    input = queue.Queue()
    output = queue.Queue()
    instances = []

    client = MongoClient(config['mongo']['ip'], config['mongo']['port'])
    dapps = config['dapps']

    initStart = time.time_ns()
    initCount = 0
    sub_infos = {}
    for k in dapps.keys():
        dapp = __import__(k, globals(), locals(), ['name', 'subscribed_receipts', 'init', 'run', 'db_namespace'])
        db = None
        if dapp.db_namespace() is not None:
            db = client[dapp.db_namespace()]
        args = {}
        if 'args' in dapps[k]:
            args = dapps[k]['args']
        for _ in range(dapps[k]['count']):
            args['signer'] = eth_sign_transaction
            args['logparser'] = parse_log
            args['priv_key'] = accounts[initCount]['priv_key']
            args['address'] = accounts[initCount]['address']
            args['balance'] = accounts[initCount]['balance']
            instances.append(DAppInstance(dapp, args, db).init())
            initCount += 1
        
        sub = dapp.subscribed_receipts(args)
        if sub['type'] != 'none':
            sub_infos[dapp.name()] = dapp.subscribed_receipts(args)
    logger.info('init %d instances in %d ns', initCount, (time.time_ns() - initStart))

    global server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    dappcontainer_pb2_grpc.add_DAppContainerServicer_to_server(DAppContainer(input), server)
    server.add_insecure_port('[::]:%d' % config['server']['port'])
    server.start()
    logger.info('server started...')

    connstr = '%s:%d' % (config['server']['ip'], config['server']['port'])
    stub = None
    with grpc.insecure_channel(config['clientsvc']) as channel:
        stub = clientsvc_pb2_grpc.ClientServiceStub(channel)
        response = register_client(connstr, stub, sub_infos)
        logger.info('RegisterClient response status %d', response.status)
    
        logger.debug('before thread pool executor')
        global quit 
        quit = threading.Event()
        with futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(receiveNewTxs, connstr, stub, output, quit)
            executor.submit(runDAppContainer, instances, input, output, quit)
            logger.debug('after thread pool executor')
            input.put({'anything':1})

            signal.signal(signal.SIGINT, sighandler)
            # server.wait_for_termination()
            signal.pause()

if __name__ == '__main__':
    acc_file_name = './accounts.txt'
    if len(sys.argv) == 2:
        acc_file_name = sys.argv[1]
    with open('./config.yml', 'r') as cf, open(acc_file_name, 'r') as af:
        config = load(cf, Loader=Loader)
        accounts = []
        for line in af:
            segments = line.split(',')
            accounts.append({
                'priv_key': segments[0],
                'address': segments[1],
                'balance': int(segments[2]),
            })
        serve(config, accounts)
