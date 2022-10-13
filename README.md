# SuperChain: 监管链场景的区块链
[English](README_en.md) | 中文
## 环境依赖
```
python>=3.8
pip install -r requirements.txt
```
## 项目结构
- common：通用组件
    - config：从./resources/config.json载入配置
    - log：向终端及./resources/log/写入日志
- cs：客户端及主服务器
    - client：模拟客户端
    - server：后端主服务器的业务部分
- framework：框架
    - factory：支持工厂模式，按照./resources/node.json配置创建对象
    - rpc：支持节点的socket通信，暂时仅支持udp
    - session：由client创建，用于client的网络部分，支持一次CS会话
- nodes：节点及节点逻辑
    - base：通用基类
    - cross：跨链节点
    - service：业务链节点
    - super：监管链节点
- resources：资源
    - config.json：配置
    - node.json：工厂要创建的对象
    - log/ 存放日志，以时间命名
- test：测试
    - connect：工厂创建节点及互相发包的RPC基础测试
    - key_distribution：TDD完成，密钥分发测试。
    - commit_log：TDD完成，日志提交测试。
## Usage
```
source env.sh

python test/commit_log.py  # 日志提交测试
python test/key_distribution.py # 密钥分发测试
python test/connect.py # 工厂模式与udp链接测试
```