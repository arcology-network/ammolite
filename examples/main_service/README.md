## MainService

### Deploy

**Usage**

python3 deploy.py \<frontend-svc-url> \<private-key>

* **frontend-svc-url**: URL of frontend service;
* **private-key**: Private key of the contract's owner, in hex string format.

Example:

```shell
$ python3 deploy.py http://localhost:8080 cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865
Deployment complete, run this command to start the test:
python3 run.py http://localhost:8080 cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865 0x1234567890123456789012345678901234567890 0x0987654321098765432109876543210987654321 0x1357924680135792468013579246801357924680
```

### Run the test

**Usage**

Copy the output of deploy.py in terminal to run the test, or type:

python3 run.py \<frontend-svc-url> \<private-key> \<storage-svc-address> \<computing-svc-address> \<main-svc-address>

* **frontend-svc-url**: URL of frontend service;
* **private-key**: Private key of the transactions' signer, in hex string format;
* **storage-svc-address**: Address of the StorageService contract;
* **computing-svc-address**: Address of the ComputingService contract;
* **main-svc-address**: Address of the MainSerivce contract.

Example:

```shell
$ python3 run.py http://localhost:8080 cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865 0x1234567890123456789012345678901234567890 0x0987654321098765432109876543210987654321 0x1357924680135792468013579246801357924680
```

Press Ctrl+C to stop the test.