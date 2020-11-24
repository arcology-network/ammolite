FROM ubuntu:20.04
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends tzdata
RUN apt install -y python3-pip autoconf libsecp256k1-dev pkg-config
RUN pip3 install py-solc-x web3 secp256k1 attrdict blocksmith PyYAML
RUN mkdir /usr/local/lib/python3.8/dist-packages/ammolite
COPY *.py tools/*.py /usr/local/lib/python3.8/dist-packages/ammolite/
RUN python3 /usr/local/lib/python3.8/dist-packages/ammolite/install_solc.py
COPY eth_account/account.py eth_account/datastructures.py /usr/local/lib/python3.8/dist-packages/eth_account/