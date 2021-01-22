import sys
import time
sys.path.append('../')

from ammolite import (Cli, HTTPProvider, Account)

cli = Cli(HTTPProvider("http://192.168.1.111:8080"))

willQuery=True
blockHeight=0
queryCount=0
while willQuery:
  block = cli.getBlock(-1)
  print(block['height'])
  if blockHeight>0 and block['height']>blockHeight:
    willQuery=False
    print('Cluster is runing.....')
  else:   
    blockHeight=block['height']  
    queryCount=queryCount+1

    if queryCount>5:
      break
    time.sleep(5)
if willQuery:
  print('Cluster status error, please contact system administrator.....')
