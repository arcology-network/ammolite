## PhoneBook

### Deploy

**Usage**

python3 deploy.py \<frontend-svc-url> \<private-key>

* **frontend-svc-url**: URL of the frontend service;
* **private-key**: Private key of the contract's owner, in hex string format.

Example:

```shell
$ python3 deploy.py http://localhost:8080 cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865
Deployment complete, run this command to start the test:
python3 run.py http://localhost:8080 accounts.txt 0x1234567890123456789012345678901234567890
```

### Run the test

**Usage**

Generate 10 accounts and write them to accounts.txt:

```shell
$ python3 accgen.py 10
```

Copy the output of deploy.py to terminal to run the test, or type:

python3 run.py \<frontend-svc-url> \<account-file> \<contract-address>

* **frontend-svc-url**: URL of frontend service;
* **account-file**: The file containing the information of accounts;
* **contract-address**: The address of the PhoneBook contract.

Example:

```shell
$ python3 run.py http://localhost:8080 accounts.txt 0x1234567890123456789012345678901234567890
```

Press Ctrl+C to stop the test.