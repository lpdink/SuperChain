import asyncio


async def receive():
    msg = 100
    while True:
        await asyncio.sleep(2)
        print(f"receive msg {msg}")
        msg -= 1


async def send():
    index = 0
    while True:
        await asyncio.sleep(1)
        print(f"send package {index}")
        index += 1


async def test():
    print("test!")
    await asyncio.sleep(1)


loop = asyncio.get_event_loop()
tasks = [receive(), send()]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
