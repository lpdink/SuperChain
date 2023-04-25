# 导入cryptography库中的ec模块和hazmat模块
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# 假设有四个节点，分别用A,B,C,D表示，每个节点都有自己的私钥和公钥
# 生成四个椭圆曲线密钥对，使用secp256k1曲线
private_key_A = ec.generate_private_key(ec.SECP256K1())
public_key_A = private_key_A.public_key()
private_key_B = ec.generate_private_key(ec.SECP256K1())
public_key_B = private_key_B.public_key()
private_key_C = ec.generate_private_key(ec.SECP256K1())
public_key_C = private_key_C.public_key()
private_key_D = ec.generate_private_key(ec.SECP256K1())
public_key_D = private_key_D.public_key()

# 假设A是主节点，B,C,D是副本节点，A发起一个提议，用自己的私钥对提议进行签名
proposal = b"Some proposal"
signature_A = private_key_A.sign(proposal, ec.ECDSA(ec.hashes.SHA256()))

# A将提议和签名发送给B,C,D，B,C,D收到后用A的公钥对签名进行验证
public_key_A.verify(signature_A, proposal, ec.ECDSA(ec.hashes.SHA256()))

# B,C,D分别用自己的私钥对提议进行投票，并将投票结果和签名发送给其他节点
vote_B = b"Agree"
signature_B = private_key_B.sign(vote_B, ec.ECDSA(ec.hashes.SHA256()))
vote_C = b"Agree"
signature_C = private_key_C.sign(vote_C, ec.ECDSA(ec.hashes.SHA256()))
vote_D = b"Disagree"
signature_D = private_key_D.sign(vote_D, ec.ECDSA(ec.hashes.SHA256()))

# 每个节点收到其他节点的投票结果和签名后，用相应的公钥对签名进行验证
public_key_B.verify(signature_B, vote_B, ec.ECDSA(ec.hashes.SHA256()))
public_key_C.verify(signature_C, vote_C, ec.ECDSA(ec.hashes.SHA256()))
public_key_D.verify(signature_D, vote_D, ec.ECDSA(ec.hashes.SHA256()))

# 如果有超过2/3的节点同意提议，则提议被确认，否则被拒绝
# 这里假设有三个节点同意提议，则提议被确认，并由A发送确认消息和签名给其他节点
confirm_A = b"Confirm"
signature_A = private_key_A.sign(confirm_A, ec.ECDSA(ec.hashes.SHA256()))

# 其他节点收到确认消息和签名后，用A的公钥对签名进行验证
public_key_A.verify(signature_A, confirm_A, ec.ECDSA(ec.hashes.SHA256()))
