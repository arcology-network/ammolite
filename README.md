# Ammolite
A framework for DApp automated-test and development.

## Introduction
Ammolite is an automated-test and development framework to meet the needs of large-scale testing for Arcology network. 
It was originally designed to help easily develop client-end logics for decentralized applications deployed
on Arcology network. 

Ammolite is capable of generating and sending large volume of complex user requests automatically into Arcology network. It is particularly useful simulating various types of user behaviors to test dAPPs. Ammolite has the following characteristics: 

*	Generality: Work with different smart contracts on Arcology network
*	Ease of use: Easy to program with python
*	High performance: Ability to simulate large volume of user requests with limited resources
*	Independence: Only interact with Arcology nodes via standard interfaces  

## Preparation
1. Install python3 and pip
> [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) is highly recommended.
2. Install dependencies:
> pip install -r requirements.txt
3. 
> cp ammolite/eth_account/account.py /your/python/lib/directory/site-packages/eth_account/
4. Start a MongoDB in the simplest way:
> docker run -P --name mymongo -d mongo