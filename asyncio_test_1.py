#!/usr/bin/env python3.5

import asyncio
import datetime
import signal
import time

async def my_coro(name, time, queue):
    while True:
        #~ print("coro-{} sleeping for {} seconds".format(name, time))
        await queue.put((name, "{} | coro-{} sleeping for {} seconds".format(datetime.datetime.now(), name, time)))
        await asyncio.sleep(time)

async def print_coro(queue):
    while True:
        #~ loop = asyncio.get_event_loop()
        #~ if not loop.is_closed():
        for i in range(queue.qsize()):
            res = await queue.get()
            print(res[1])
            #~ queue.task_done()
        await asyncio.sleep(2)
    #~ await print_coro(queue)

async def main_coro(stop):
    queue = asyncio.PriorityQueue()
    asyncio.gather(my_coro(1, 1, queue), my_coro(2, 2, queue), print_coro(queue))
    await stop

loop = asyncio.get_event_loop()
stop = loop.create_future()
loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
loop.add_signal_handler(signal.SIGINT, stop.set_result, None)

start_time = time.monotonic()
#~ loop.run_until_complete(asyncio.gather(my_coro(stop, "one", 1, 8), my_coro(stop, "two", 2, 4)))
loop.run_until_complete(main_coro(stop))
#~ loop.run_forever()
total_time = time.monotonic() - start_time
print("total time: ", total_time)

loop.close()
