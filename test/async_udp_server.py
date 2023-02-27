"""
Author: lpdink
Date: 2022-10-09 16:03:12
LastEditors: lpdink
LastEditTime: 2022-10-09 16:04:20
Description: UDP服务器，reference from https://docs.python.org/zh-cn/3/library/asyncio-protocol.html
"""
import asyncio
import time


class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
        self.count = 0
        self.start = 0
        self.end = 0

    def datagram_received(self, data, addr):
        # message = data.decode()
        # print("Received %r from %s" % (message, addr))
        # print("Send %r to %s" % (message, addr))
        # self.transport.sendto(data, addr)
        if self.count==0:
            self.start = time.perf_counter()
        if self.count>=500000:
            self.end = time.perf_counter()
            print(f"use time:{self.end-self.start} s")
            self.count=0
            self.start=time.perf_counter()
        self.count+=1


async def main():
    print("Starting UDP server")

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(), local_addr=("127.0.0.1", 9999)
    )

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()


asyncio.run(main())
