# 使用PySchnorr库
from pyschnorr import SchnorrGroup, SchnorrSignature

# 创建一个Schnorr群
group = SchnorrGroup()

# 生成一个私钥和一个公钥
private_key = group.gen_private_key()
public_key = group.gen_public_key(private_key)

# 创建一个签名对象
signer = SchnorrSignature(group)

# 签名一条消息
message = b"Hello world"
signature = signer.sign(message, private_key)

# 验证签名是否有效
valid = signer.verify(message, signature, public_key)
print(valid) # True

# 使用python-schnorr库
from schnorr import Schnorr

# 创建一个Schnorr对象
schnorr = Schnorr()

# 生成一个私钥和一个公钥
private_key = schnorr.gen_private_key()
public_key = schnorr.gen_public_key(private_key)

# 签名一条消息
message = b"Hello world"
signature = schnorr.sign(message, private_key)

# 验证签名是否有效
valid = schnorr.verify(message, signature, public_key)
print(valid) # True
