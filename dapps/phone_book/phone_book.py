from web3.auto import w3 
from web3.logs import IGNORE
from secp256k1 import PrivateKey
import logging

abi = '''
[
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "address",
				"name": "addr",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "no",
				"type": "uint256"
			}
		],
		"name": "PhoneNoQuery",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "address",
				"name": "addr",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "no",
				"type": "uint256"
			}
		],
		"name": "PhoneNoUpdated",
		"type": "event"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "address",
				"name": "addr",
				"type": "address"
			}
		],
		"name": "get",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "uint256",
				"name": "phoneNo",
				"type": "uint256"
			}
		],
		"name": "set",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
'''

def name():
    return 'phone_book'

def subscribed_receipts(args):
    return {
        'type': 'contract',
        'value': bytes(bytearray.fromhex(args['contract_address'])),
    }

def db_namespace():
    return None

def init(args, context, db):
    context['nonce'] = 0
    context['txhash'] = None
    if 'priv_key' in args:
        context['priv_key'] = PrivateKey(bytes(bytearray.fromhex(args['priv_key'])), raw=True)
    else:
        context['priv_key'] = PrivateKey()
    context['contract'] = w3.eth.contract(address=bytes(bytearray.fromhex(args['contract_address'])), abi=abi)

def run(args, context, db, receipts):
	logger = logging.getLogger('phone_book.run')
	logger.debug("step 0")
	if context['txhash'] != None:
		if context['txhash'] in receipts:
			receipt = receipts[context['txhash']]
			logger.info('receipt: %s', str(receipt))
			if receipt.status != 1:
				logger.warn('Failed to execute last transaction, receipt.status = %d', receipt.status)
			else:
				logs = args['logparser'](context['contract'].events.PhoneNoUpdated(), receipt)
				logger.debug('logs: %s', str(logs))
		else:
			logger.info("No receipts received")
	logger.debug("step 1")
	tx = context['contract'].functions.set(123).buildTransaction({
		'nonce': context['nonce'],
		'gas': 1000000,
        'gasPrice': 1,
        'chainId': 1,
	})
	logger.debug("step 2")
	tx['data'] = bytearray.fromhex(tx['data'][2:])

	tx = args['signer'](tx, context['priv_key'])
	logger.debug("step 3")

	context['nonce'] += 1
	context['txhash'] = tx['hash']
	logger.debug("step 4")
	return [tx]
