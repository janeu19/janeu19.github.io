import websockets
import asyncio
import time

PORT = 8080

# A set of connected ws clients
connected = list()
banned_IPs = dict()
unban_time = 10
client_id = 1


# The main behavior function for this server
async def echo(websocket, path):
    global client_id
    # don't let the exiled ones in
    client_ip = websocket.remote_address[0]
    print(f"incoming ip: {websocket.remote_address} current id: {client_id}")
    print(f"A client just connected + {banned_IPs}")
    if client_ip in banned_IPs.keys():
        if not check_if_unban(client_ip=client_ip):
            return
        else:
            await websocket.send("SERVER_MESSAGE: Unbanned.")

    # Store a copy of the connected client
    connected.append((client_id, websocket))
    client_id += 1
    # Handle incoming messages
    try:
        async for message in websocket:
            print("Received message from client: " + message)
            # ban Rum
            if message == "Rum":
                await ban(websocket=websocket)
                return

            # get current sender's id to use as a name
            current_id = 0
            for clients in connected:
                if clients[1] == websocket:
                    current_id = clients[0]
                    break

            for conn in connected:
                print(f"sending to {conn[0]}")
                await conn[1].send(f"{current_id} said: {message}")

    # Handle disconnecting clients
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    finally:
        await disconnect(websocket)


async def disconnect(websocket):
    print("disconnected")
    for client in connected:
        if client[1] == websocket:
            connected.remove(client)
            await websocket.close()


async def ban(websocket):
    print("banned")
    await websocket.send("SERVER_MESSAGE: Banned.")
    banned_IPs[websocket.remote_address[0]] = time.time()
    await disconnect(websocket)


def check_if_unban(client_ip):
    if time.time() - banned_IPs[client_ip] > unban_time:
        banned_IPs.__delitem__(client_ip)
        print(f"unbanned: {client_ip}")
        return True

    return False


if __name__ == "__main__":
    start_server = websockets.serve(echo, "0.0.0.0", PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()