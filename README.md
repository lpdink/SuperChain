# SuperChain: 监管链场景的区块链
[English](README_en.md) | 中文
## 环境依赖
```
python>=3.8
```
## 项目结构
```
- common # 通用组件
    - config # 从./resources/config.json载入配置
    - log # 向终端及./resources/log/写入日志
- framework # 框架
    - factory # 支持工厂模式，按照./resources/node.json配置创建对象
    - rpc # 支持节点的socket通信，暂时仅支持udp
- nodes # 节点及节点逻辑
    - base # 通用基类
    - cross # 跨链节点
    - service # 业务链节点
    - super # 监管链节点
- resources # 资源
    - config.json # 配置及要创建的对象
    - log/ 存放日志，以时间命名
- 
```