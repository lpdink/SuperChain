import asyncio
import json

# 要有主动设置超时器的能力.

class TestProtocol:
    def connection_made(self, transport):
        self.transport = transport
        self.reset = True
        print("connection made")

    def datagram_received(self, data, addr):
        self.reset = False
        print("reset set false.")

    def transfer(self):
        if self.reset:
            print("reset!")


class Node:
    def __init__(self, protocol) -> None:
        self.protocol = protocol
        self.addr = ("127.0.0.1", 65000)

    def run(self):
        asyncio.run(self.run_node())

    async def run_node(self):
        loop = asyncio.get_running_loop()
        transport, protocol_obj = await loop.create_datagram_endpoint(
            lambda: self.protocol(), local_addr=self.addr
        )
        # print(protocol_obj)
        # print(type(protocol_obj))
        # print(dir(protocol_obj))
        while True:
            protocol_obj.reset = True
            # msg = {"dont":1}
            # msg = json.dumps(msg).encode("utf-8")
            # transport.sendto(msg, self.addr)
            await asyncio.sleep(10)
            protocol_obj.transfer()
            # msg = {"reset":1}
            # msg = json.dumps(msg).encode("utf-8")
            # transport.sendto(msg, self.addr)
        # try:
        #     await asyncio.sleep(60 * 60 * 24)  # Serve for 1 day.
        # finally:
        #     transport.close()
if __name__=="__main__":
    node = Node(TestProtocol)
    node.run()