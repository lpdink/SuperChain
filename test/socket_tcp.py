# Echo client program
import socket

HOST = '127.0.0.1'    # The remote host
PORT = 8888              # The same port as used by the server
for i in range(10):
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.bind(("127.0.0.1", 12610))
    s1.connect((HOST, PORT))
    s1.sendall(b"i"*i)
    s1.shutdown(socket.SHUT_RDWR)
    s1.close()
# s1.connect((HOST, PORT))
# s2.connect((HOST, PORT))
# s1.sendall(b"i am s1")
# s1.sendall(b"i am s1 two!")
# s2.sendall(b"i am s2")
# data1 = s1.recv(1024)
# data2 = s2.recv(1024)
# print(data1, data2)
# s1.close()
# s2.close()
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b'Hello, world')
#     data = s.recv(1024)
# print('Received', repr(data))