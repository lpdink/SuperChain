import create_keypair as ckp
import schnorr_lib as sl
import os
import time

run_times = 100

user = ckp.create_keypair(1)["users"]

M = os.urandom(250)
M = sl.sha256(M)

sig = sl.schnorr_sign(M, user[0]["privateKey"])

pubkey_bytes = bytes.fromhex(user[0]["publicKey"])
# print("Signature =",sig.hex())

sig_bytes = sig
start = time.perf_counter()
for _ in range(run_times):
    result = sl.schnorr_verify(M, pubkey_bytes, sig_bytes)
end = time.perf_counter()
print(end-start)
print(result)