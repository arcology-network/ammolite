from ammolite.eth import Eth

class Cli:
    provider = None

    eth: Eth

    def __init__(self, provider):
        self.provider = provider
        self.eth = Eth()

    def sendTransactions(self, txs):
        data = {}
        for k, v in txs.items():
            data[k.hex()] = v.hex()
        r = self.provider.make_request('POST', 'txs', data)
        # print('response = {}'.format(r))
        if r.status_code != 200:
            print(r.text)

    def getBalance(self, address, **kwargs):
        data = {}
        for k, v in kwargs.items():
            if k == 'height':
                data['height'] = v
            else:
                assert False
        r = self.provider.make_request('GET', 'balances/' + address, data)
        if r.status_code != 200:
            print(r.text)
            return -1
        
        return r.json()['balance']

    def getTransactionReceipts(self, hashes):
        hashes_str = ''
        for tx_hash in hashes:
            if isinstance(tx_hash, bytes):
                tx_hash = tx_hash.hex()
            hashes_str += tx_hash + ','
        r = self.provider.make_request('GET', 'receipts/' + hashes_str[:len(hashes_str)-1], {})
        if r.status_code != 200:
            print(r.text)
            return {}
        
        return r.json()['receipts']

    def getBlock(self, height):
        r = self.provider.make_request('GET', 'blocks/' + str(height), {})
        if r.status_code != 200:
            print(r.text)
            return {}
        
        return r.json()['block']

    def getContainerAt(self, address, id, key, type, **kwargs):
        data = {'type': type}
        for k, v in kwargs.items():
            if k == 'height':
                data['height'] = v
            else:
                assert False
        r = self.provider.make_request('GET', 'containers/' + address + '/' + id + '/' + key, data)
        if r.status_code != 200:
            print(r.text)
            return {}

        return r.json()['data']
