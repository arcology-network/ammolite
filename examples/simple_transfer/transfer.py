import sys
sys.path.append('../../..')

from ammolite import (Account)

frontend = sys.argv[1]
accounts_file = sys.argv[2]
num_ktxs = int(sys.argv[3])
output = sys.argv[4]

private_keys = []
addresses = []
with open(accounts_file, 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        segments = line.split(',')
        private_keys.append(segments[0])
        addresses.append(segments[1])

num_per_batch = 1000
lines = []

def make_one_batch(i):
    keys = private_keys[i * num_per_batch : (i + 1) * num_per_batch]
    addrs = addresses[i * num_per_batch : (i + 1) * num_per_batch]
    for i in range(int(num_per_batch/2)):
        acc1 = Account(keys[i])
        acc2 = Account(keys[num_per_batch - 1 - i])
        raw_tx, tx_hash = acc1.sign({
            'nonce': 0,
            'value': 1,
            'gasPrice': 1,
            'gas': 21000,
            'to': bytes(bytearray.fromhex(addrs[num_per_batch - 1 - i][2:])),
            'data': b'',
        })
        lines.append('{},{}\n'.format(raw_tx.hex(), tx_hash.hex()))

        raw_tx, tx_hash = acc2.sign({
            'nonce': 0,
            'value': 1,
            'gasPrice': 1,
            'gas': 21000,
            'to': bytes(bytearray.fromhex(addrs[i][2:])),
            'data': b'',
        })
        lines.append('{},{}\n'.format(raw_tx.hex(), tx_hash.hex()))

for i in range(num_ktxs):
    make_one_batch(i)

with open(output, 'w') as f:
    for l in lines:
        f.write(l)
