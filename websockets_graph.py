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

conns = set()

x_spacing = TOTAL_W / NUM_POINTS
x_vals = [i * x_spacing + (x_spacing / 2) + MARGIN for i in range(NUM_POINTS)]

y_vals = deque(maxlen = NUM_POINTS)
for i in range(NUM_POINTS):
    y_vals.append(TOTAL_H)
    
#~ vals_combined = []
vals_out = ""

async def ws_send(websocket, path):
    conns.add(websocket)
    print(conns)
    try:
        while True:        
            #~ load_avg = os.getloadavg()[0] / 4
            #~ if load_avg > 1:
                #~ load_avg = 1
            #~ vals_combined = []
            #~ y_vals.append(TOTAL_H - (load_avg * TOTAL_H) + MARGIN)
            
            vals_combined = []
            for i in zip(x_vals, y_vals):
                vals_combined.append(str(i[0]) + "," + str(i[1]))
            vals_out = " ".join(vals_combined)
            
            #~ await websocket.send(json.dumps(list(y_vals)))
            await websocket.send(json.dumps(vals_out))
            await asyncio.sleep(2)
    except websockets.exceptions.ConnectionClosed:
        #~ pass
        await websocket.close()
    finally:
        conns.remove(websocket)

async def get_data():
    while True:
        load_avg = os.getloadavg()[0] / 4
        if load_avg > 1:
            load_avg = 1
        #~ vals_combined = []
        y_vals.append(TOTAL_H - (load_avg * TOTAL_H) + MARGIN)
        await asyncio.sleep(2)

async def main_coro(websocket, path):
    conns.add(websocket)
    print(conns)
    while True:
        asyncio.gather(ws_send(websocket, path), get_data())

async def sock_server():
    print("Starting server...")
    server = websockets.serve(ws_send, '127.0.0.1', 5678)
    #~ async with websockets.serve(ws_send, '127.0.0.1', 5678):
    #~ async with websockets.serve(ws_send, '127.0.0.1', 5678):
        #~ pass
    print("\nShutting down server")

def sig_handle(loop, tasks):
    tasks.cancel()
    #~ for task in asyncio.Task.all_tasks():
        #~ task.cancel()
    print("\nstopping event loop")
    loop.stop()

loop = asyncio.get_event_loop()
server = websockets.serve(ws_send, '127.0.0.1', 5678)
tasks = asyncio.gather(server, get_data())

loop.add_signal_handler(signal.SIGTERM, sig_handle, loop, tasks)
loop.add_signal_handler(signal.SIGINT, sig_handle, loop, tasks)

#~ loop.run_until_complete(sock_server(stop))

#~ asyncio.gather(sock_server(), get_data())
#~ loop.run_until_complete(server)

try:
    loop.run_forever()
finally:
    loop.close()
    print("loop closed")
