## Performance Test Guide

### Deploy ParallelKitties

```shell
$ ./deploy_pk.sh
```

### Initialize test data

```shell
$ ./send_init_txs.sh
```

### Test ParallelKitties' Transfer function

```shell
$ ./send_pk_transfer_txs.sh
```

### Test balance transfer between accounts

```shell
$ ./send_simple_transfer_txs.sh
```

### Check TPS

```shell
$ ./tps.sh
```
 