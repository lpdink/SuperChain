from common import logging, config
import socket
import json


class Rpc():
    def __init__(self, addr=None, config=config.connection) -> None:
        # socket.SOCK_DGRAM UDP
        # socket.SOCK_STREAM TCP
        self.config = config
        timeout = config.get("timeout", None)
        if self.config.use_tcp:
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if addr is not None:
            self.bind(addr)
        else:
            # if addr not set, use localhost and random port.
            self.bind(("127.0.0.1", 0))
        if timeout is not None:
            self.set_timeout(timeout)

    @property
    def addr(self):
        return self.sk.getsockname()

    @property
    def port(self):
        return self.sk.getsockname()[1]

    def bind(self, addr):
        try:
            self.sk.bind(tuple(addr))
            logging.info(f"addr {self.addr} is binded")
            return True
        except OSError as e:
            logging.warning(f"addr {self.addr} bind failed: {e}")
            return False

    def set_timeout(self, timeout):
        self.sk.settimeout(timeout)
        logging.info(f"addr {self.addr} set timeout {timeout}")

    def send(self, data, addr):
        data = json.dumps(data).encode("utf-8")
        if self.config.use_tcp:
            self.sk.connect(tuple(addr))
            self.sk.sendall(data)
        else:
            self.sk.sendto(data, tuple(addr))
            logging.info(f"{self.addr} node send {data} to {addr}")

    def recv(self):
        recv_max_bytes = self.config.get("recv_max_bytes", 65535)
        data, addr = self.sk.recvfrom(recv_max_bytes)
        return json.loads(data), addr

    def close(self):
        self.sk.close()


if __name__ == "__main__":
    # logging.info("in rpc")
    from common.config import config
    from multiprocessing import Process
    import time
    rpc1 = Rpc(("127.0.0.1", 10001), config.connection)
    rpc2 = Rpc(("127.0.0.1", 10002), config.connection)

    def listen(rpc: Rpc):
        while True:
            try:
                data, addr = rpc.recv()
            except:
                data, addr = {}, None
            if addr is not None:
                print(f"{rpc.addr} receive {data} from addr {addr}")

    def send(rpc: Rpc, addr):
        index = 0
        while True:
            rpc.send({"package": index}, addr)
            time.sleep(1)
            index += 1

    p1 = Process(target=listen, args=(rpc1,))
    p2 = Process(target=listen, args=(rpc2,))
    p3 = Process(target=send, args=(rpc1, ("127.0.0.1", 10002)))
    p4 = Process(target=send, args=(rpc2, ("127.0.0.1", 10001)))
    pool = [p1, p2, p3, p4]
    for p in pool:
        p.start()
    for p in pool:
        p.join()
