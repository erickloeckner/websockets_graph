#!/usr/bin/env python3.6

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

x_spacing = TOTAL_W / NUM_POINTS
x_vals = [i * x_spacing + (x_spacing / 2) + MARGIN for i in range(NUM_POINTS)]

y_vals = deque(maxlen = NUM_POINTS)
for i in range(NUM_POINTS):
    y_vals.append(TOTAL_H)
    
#~ vals_combined = []
vals_out = ""

async def ws_send(websocket, path):
    try:
        while True:        
            load_avg = os.getloadavg()[0] / 4
            if load_avg > 1:
                load_avg = 1
            vals_combined = []
            y_vals.append(TOTAL_H - (load_avg * TOTAL_H) + MARGIN)
            
            for i in zip(x_vals, y_vals):
                vals_combined.append(str(i[0]) + "," + str(i[1]))
            vals_out = " ".join(vals_combined)
            
            #~ await websocket.send(json.dumps(list(y_vals)))
            await websocket.send(json.dumps(vals_out))
            await asyncio.sleep(2)
    except websockets.exceptions.ConnectionClosed:
        pass


async def sock_server(stop):
    print("Starting server...")
    async with websockets.serve(ws_send, '127.0.0.1', 5678):
        await stop
        print("\nShutting down server")
#~ start_server = websockets.serve(ws_send, '127.0.0.1', 5678)

#~ asyncio.get_event_loop().run_until_complete(start_server)
#~ asyncio.get_event_loop().run_forever()

loop = asyncio.get_event_loop()
stop = loop.create_future()
loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
loop.add_signal_handler(signal.SIGINT, stop.set_result, None)

loop.run_until_complete(sock_server(stop))
loop.close()
