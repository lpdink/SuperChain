from cryptography.hazmat.primitives import hashes, hmac
key = b'test key. Beware! A real key should use os.urandom or TRNG to generate'
h = hmac.HMAC(key, hashes.SHA256())
h.update(b"message to hash")
signature = h.finalize()
# -----------------------
verify_h = hmac.HMAC(key, hashes.SHA256()) # verify_hmac, key与line3相同
verify_h.update(b"message to hash") # Line8是必须的，且消息体需要与line4相同。
verify_h.verify(signature) # success