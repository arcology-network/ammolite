import blocksmith
import sys
import random

count = int(sys.argv[1])

kg = blocksmith.KeyGenerator()
kg.seed_input('This is the seed.')

with open('./accounts.txt', 'w') as full, open('./addresses.txt', 'w') as addr:
    for i in range(count):
        private_key = kg.generate_key()
        address = blocksmith.EthereumWallet.generate_address(private_key)
        checksum_address = blocksmith.EthereumWallet.checksum_address(address)
        balance = random.randrange(10, 1000) * 1e18
        full.write('%s,%s,%d\n' % (private_key, checksum_address, balance))
        addr.write('%s,%d\n' % (checksum_address, balance))