"""
Author: lpdink
Date: 2022-10-09 12:25:19
LastEditors: lpdink
LastEditTime: 2022-10-09 15:57:03
Description: reference from https://docs.python.org/zh-cn/3/library/asyncio-protocol.html，官方文档。
令人诧异，EchoClientProtocol实际上被要求实现asyncio.protocols.DatagramProtocol的必要方法，但文档中没有进行继承。
The user should implement this interface.  They can inherit from
    this class but don't need to.  The implementations here do
    nothing (they don't raise exceptions).
"""
import asyncio


class EchoClientProtocol:
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print("Send:", self.message)
        self.transport.sendto(self.message.encode())

    def datagram_received(self, data, addr):
        print("Received:", data.decode())

        print("Close the socket")
        self.transport.close()

    def error_received(self, exc):
        print("Error received:", exc)

    def connection_lost(self, exc):
        print("Connection closed")
        self.on_con_lost.set_result(True)


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    message = "Hello World!"

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoClientProtocol(message, on_con_lost),
        remote_addr=("127.0.0.1", 9999),
    )

    try:
        await on_con_lost
    finally:
        transport.close()


asyncio.run(main())
