#!/usr/bin/env python3.5

import asyncio
import datetime
import json
import os
import random
import signal
import websockets
from collections import deque

NUM_POINTS = 100
TOTAL_W = 1260
TOTAL_H = 700
MARGIN = 10
TIME_DELAY = 5

conns = set()

x_spacing = TOTAL_W / NUM_POINTS
x_vals = [i * x_spacing + (x_spacing / 2) + MARGIN for i in range(NUM_POINTS)]

y_vals = deque(maxlen = NUM_POINTS)
for i in range(NUM_POINTS):
    y_vals.append(TOTAL_H)
    
vals_out = ""

async def ws_send(websocket, path):
    #~ conns.add(websocket)
    #~ print(conns)
    try:
        while True:
            vals_combined = []
            for i in zip(x_vals, y_vals):
                vals_combined.append(str(i[0]) + "," + str(i[1]))
            vals_out = " ".join(vals_combined)
            
            #~ await websocket.send(json.dumps(list(y_vals)))
            await websocket.send(json.dumps(vals_out))
            await asyncio.sleep(TIME_DELAY)
    except websockets.exceptions.ConnectionClosed:
        await websocket.close()
    finally:
        #~ conns.remove(websocket)
        pass

async def get_data(stop):
    while not stop.done():
        load_avg = os.getloadavg()[0] / 4
        if load_avg > 1:
            load_avg = 1
        y_vals.append(TOTAL_H - (load_avg * TOTAL_H) + MARGIN)
        await asyncio.sleep(TIME_DELAY)

async def sock_server(stop):
    print("Starting server")
    async with websockets.serve(ws_send, '127.0.0.1', 5678):
        await stop
    print("\nShutting down server")

async def main_coro(stop):
    await asyncio.gather(sock_server(stop), get_data(stop))

def main():
    loop = asyncio.get_event_loop()
    stop = loop.create_future()

    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    
    loop.run_until_complete(main_coro(stop))
    loop.close()

if __name__ == "__main__":
    main()
