import json
import base64
# import copy
from eth_hash.auto import keccak

def toHexString(value, aligned_left):
    hexStr = ''
    if type(value) is int:
        hexStr = hex(value)[2:]
    elif type(value) is bytes:
        hexStr = value.hex()
    elif type(value) is str:
        if value[:2] == '0x':
            hexStr = value[2:]
        else:
            hexStr = value
    else:
        assert False
    if aligned_left:
        return hexStr + '0' * (64 - len(hexStr))
    else:
        return '0' * (64 - len(hexStr)) + hexStr

def encodeArguments(abi_inputs, args):
    if len(abi_inputs) != len(args):
        assert False
    data = ''
    index = 0
    offset = len(args)
    vars = []
    for input in abi_inputs:
        if (str.startswith(input['type'], 'uint') or str.startswith(input['type'], 'int')) and input['type'][-2:] != '[]':
            data += toHexString(args[index], False)
        elif input['type'] == 'address':
            data += toHexString(args[index], False)
        elif str.startswith(input['type'], 'bytes') and input['type'][-2:] != '[]':
            data += toHexString(offset * 16, False)
            offset += int((len(args[index]) - 1) / 32) + 1
            vars.append(args[index])
        else:
            assert False
        index += 1
    for v in vars:
        data += toHexString(len(v), False)
        data += toHexString(v, True)
    return data

class ContractConstructor:
    data: str
    tx = {
        'to': b'',
        'value': 0,
        'gas': 21000,
        'gasPrice': 1,
        'nonce': 0,
    }

    def __init__(self, bytecode):
        self.data = bytecode

    def __call__(self, *args, **kwargs) -> 'ContractConstructor':
        data = self.data
        for arg in args:
            if type(arg) is int:
                hexInt = hex(arg)[2:]
                data += '0' * (64-len(hexInt)) + hexInt
            elif type(arg) is bytes:
                hexBytes = arg.hex()
                data += '0' * (64-len(hexBytes)) + hexBytes
            elif type(arg) is str:
                if arg[:2] == '0x':
                    arg = arg[2:]
                data += '0' * (64-len(arg)) + arg
            else:
                # print(args)
                assert False
        self.tx['data'] = bytes(bytearray.fromhex(data))
        # print("data = {}, args = {}".format(self.data, args))
        return self

    def buildTransaction(self, params):
        tx = self.tx
        for k, v in params.items():
            tx[k] = v
        return tx

class ContractFunction:
    data: str
    address: str
    tx = {
        'to': b'',
        'value': 0,
        'gas': 21000,
        'gasPrice': 1,
        'nonce': 0,
    }

    def __init__(self, address, signature):
        self.address = address
        self.data = signature

    def __call__(self, *args, **kwargs) -> 'ContractFunction':
        data = self.data
        for arg in args:
            if type(arg) is int:
                hexInt = hex(arg)[2:]
                data += '0' * (64-len(hexInt)) + hexInt
            elif type(arg) is bytes:
                hexBytes = arg.hex()
                data += '0' * (64-len(hexBytes)) + hexBytes
            elif type(arg) is str:
                if arg[:2] == '0x':
                    arg = arg[2:]
                data += '0' * (64-len(arg)) + arg
            else:
                # print(args)
                assert False
        self.tx['data'] = bytes(bytearray.fromhex(data))
        self.tx['to'] = bytes(bytearray.fromhex(self.address))
        # print("address = {}, data = {}, args = {}".format(self.address, self.data, args))
        return self

    def buildTransaction(self, params):
        tx = self.tx
        for k, v in params.items():
            tx[k] = v
        # print(tx)
        return tx

class ContractFunctions:
    abi: str
    address: str

    def __init__(self, abi, address):
        self.abi = abi
        self.address = address

    def __getattr__(self, name):
        for item in self.abi:
            if item['type'] == 'function' and item['name'] == name:
                signature = name + '('
                for i in item['inputs']:
                    signature += i['type'] + ','
                if len(item['inputs']) == 0:
                    signature += ')'
                else:
                    signature = signature[:len(signature)-1] + ')'
                # print('signature = %s, hex = %s' % (signature, keccak(bytearray(signature, 'ascii'))[:4].hex()))
                return ContractFunction(self.address, keccak(bytearray(signature, 'ascii'))[:4].hex())
        
        assert False

class Contract:
    abi = None
    bytecode = None
    address = None
    events = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'abi':
                self.abi = v
            elif k == 'bytecode':
                self.bytecode = v
            elif k == 'address':
                if v[:2] == '0x':
                    v = v[2:]
                self.address = v
            else:
                assert False
        
        if self.abi is None:
            assert False
        
        for item in self.abi:
            if item['type'] != 'event':
                continue

            indexed = []
            indexless = []
            signature = item['name'] + '('
            for i in item['inputs']:
                signature += i['type'] + ','
                if i['indexed']:
                    indexed.append(i['name'])
                else:
                    indexless.append(i['name'])

            if len(item['inputs']) == 0:
                signature += ')'
            else:
                signature = signature[:len(signature)-1] + ')'

            self.events[keccak(bytearray(signature, 'ascii')).hex()] = {
                'name': item['name'],
                'indexed': indexed,
                'indexless': indexless,
            }

    def __getattr__(self, name):
        if name == "constructor":
            if self.abi is None or self.bytecode is None:
                assert False
            return ContractConstructor(self.bytecode)

        if name == "functions":
            if self.abi is None or self.address is None:
                assert False
            return ContractFunctions(self.abi, self.address)

    def processReceipt(self, receipt):
        if 'logs' not in receipt or receipt['logs'] is None:
            return {}
        events = {}
        for log in receipt['logs']:
            if log['address'] != self.address:
                continue
            
            signature = log['topics'][0]
            if signature not in self.events:
                continue

            args = {}
            index = 1
            for i in self.events[signature]['indexed']:
                args[i] = log['topics'][index]
                index += 1
            index = 0
            for i in self.events[signature]['indexless']:
                args[i] = log['data'][index*64:(index+1)*64]
                index += 1
            events[self.events[signature]['name']] = args
        return events

    def setAddress(self, address):
        if address[:2] == '0x':
            address = address[2:]
        self.address = address
