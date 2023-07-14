# SuperChain: 监管链场景的区块链
[English](README_en.md) | 中文
## 环境依赖
```
python>=3.8
pip install -r requirements.txt
```
## Usage
```
# run server
python consensus_server.py

# 测试tps:
python consensus_client.py

# 或者交互式的终端：
python cmd_client.py
```

## 配置说明

可以修改SuperChain/resources/consensus_node.json中的nums来决定起多少个区块链节点，由于满二叉树+一个信箱的设计，需要是偶数。  
可以修改SuperChain/resources/config.json中的consensus.batch_size(由于tcp通信报文大小限制，不要超过256)和n包压一包配置：consensus.package_size（单机测试不要过大，否则网卡扛不住）  