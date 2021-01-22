FROM ubuntu:20.04
RUN apt update
RUN apt-get install -y openssh-server
EXPOSE 22
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends tzdata
RUN apt install -y python3-pip autoconf libsecp256k1-dev pkg-config
RUN pip3 install py-solc-x web3 secp256k1 attrdict blocksmith PyYAML rich
RUN mkdir /usr/local/lib/python3.8/dist-packages/ammolite
COPY *.py tools/*.py /usr/local/lib/python3.8/dist-packages/ammolite/
RUN python3 /usr/local/lib/python3.8/dist-packages/ammolite/install_solc.py
COPY eth_account/account.py eth_account/datastructures.py /usr/local/lib/python3.8/dist-packages/eth_account/
RUN mkdir ~/contract
COPY examples/parallel_kitties/contract/* ~/contract/
COPY examples/parallel_kitties/*.sh examples/parallel_kitties/deploy_v2.py examples/parallel_kitties/sendtxs.py ~/
RUN mkdir /run/sshd
RUN echo 'root:frY6CvAy8c9E' | chpasswd
RUN sed -ri 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config
RUN mkdir /root/.ssh
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
CMD ["/usr/sbin/sshd", "-D"]