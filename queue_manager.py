import asyncio

queue = asyncio.Queue()

async def worker():
    while True:
        func, args = await queue.get()
        try:
            await func(*args)
        except Exception as e:
            print(e)
        queue.task_done()

def start_workers(n=2):
    for _ in range(n):
        asyncio.create_task(worker())