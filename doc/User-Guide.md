## ammolite User Guide

### Overview

ammolite是一套旨在提升DApps开发和智能合约测试效率的开发框架，允许用户通过Python脚本实现定制化的DApps逻辑，并与Monaco网络进行交互。它提供的主要功能包括：

* 收集用户脚本产生的交易，将他们发送给Monaco网络完成处理；
* 允许用户脚本对特定交易或交易组执行后产生的receipts进行订阅，并在这些receipts可用后将它们推送给用户；
* 维护用户脚本的输入参数、上下文，并提供了一个MongoDB句柄来支持用户脚本完成持久化操作。

为了简化用户脚本的开发，ammolite定义了一组接口，任何一个用户脚本只要实现了这组接口，就可以在ammolite框架中托管运行，并允许用户针对同一个脚本启动多个实例。

### Interface Specification

用户脚本使用Python语言开发，需要实现的方法如下：

```python
# 返回DApp的名称，这个名称在ammolite中用于识别不同的DApps。
def name():

# 返回该合约的receipts订阅说明，返回值是一个map，其中必须包含的key是“type”，“type”支持三种取值：
# “contract” - 订阅所有对某一合约地址的调用，合约地址通过“value”字段指定；
# “tx” - 订阅所有由该客户端实例产生的交易；
# “none” - 不订阅任何receipts。
def subscribed_receipts():

# 返回该合约使用的MongoDB数据库名称，多个相关的客户端脚本通过返回相同的数据库名称可以共享同一个数据库。
def db_namespace():

# 在一个实例初始化时调用，传入参数包括：
# args - 该实例的启动参数，类型是map，其中包括以下字段：
#   signer - 用于执行交易签名的函数句柄，参数为（tx，priv_key），tx为未签名的交易，priv_key为私钥；
#   priv_key - 32字节的私钥；
#   address - 20字节的地址；
#   balance - 账户初始余额。
#   以及其他用户通过配置文件提供的自定义参数（这部分目前还没有实现）；
# context - 该实例的上下文，类型是map，同一脚本的不同实例具有独立的上下文；
# db - pymongo的Database句柄，用于用户脚本与数据库之间交互。
def init(args, context, db):

# 该函数在每一个新块产生后调用，前三个参数与init含义相同，receipts类型为map，key为交易哈希，value为receipt对象。
# 包含从上一次调用到本次调用之间产生的所有该应用订阅的receipts。
# 该函数的返回值为交易列表，类型为array，其中的每一个元素表示一个交易，交易的类型为map，包含以下字段：
# raw - 通过签名并进行RLP encode的raw transaction；
# hash - 交易哈希；
# to - 交易的接收方地址。
# 后两个字段并不是发起交易所必须的，这两个字段主要是提供给client-svc，用于receipts分发逻辑。否则client-svc就需要
# 对raw transaction进行RLP decode和签名验证后才能获取这些信息。
def run(args, context, db, receipts):
```

### Configuration

客户端脚本一般存放在ammolite的dapps路径下，例如：

```
ammolite
  |-- dapps
        |-- transfer.py
        |-- ecommerce
              |-- platform.py
              |-- buyer.py
              |-- seller.py
```

客户端脚本可以直接存储在dapps路径下，也可以嵌套文件夹对复杂脚本进行组织。脚本准备就绪后，通过修改ammolite的config.yml配置文件可以对启动的脚本及实例数进行设定，ammolite运行所需的其他参数也包含在其中。

```YAML
# ammolite的GRPC连接设置，为了接收client-svc推送的receipts，
# ammolite实现了一组GRPC接口。
server: {ip: localhost, port: 50001}
# client-svc连接设置
clientsvc: localhost:50000
# DApps设置，下列设置表示：为dapps路径下的transfer.py脚本启动2个
# 实例；为dapps/ecommerce路径下的platform.py脚本启动1个实例。
dapps: {dapps.transfer: 2, dapps.ecommerce.platform: 1}
# ammolite使用的MongoDB连接设置。
mongo: {ip: localhost, port: 32768}
```
