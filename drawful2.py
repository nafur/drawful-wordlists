import asyncio
import json
import logging
import requests
import ssl
import time
import websockets

logger = logging.getLogger(__name__)

APPID = "8511cbe0-dfff-4ea9-94e0-424daad072c3"
NAME = "GEREON"
UID = "5e3c1f2e-abf3-419c-966c-c2afb432c7f8"

class Client:
    def __init__(self, uid, room):
        self.__uid = uid
        self.__room = room

    async def __recv(self):
        msg = await self.ws.recv()
        logger.debug("Received %s" % msg)
        msg = msg.split(":", 3)
        code = int(msg[0])
        if code == 1:
            self.on_connect()
        elif code == 5:
            data = json.loads(msg[3])["args"][0]
            mtype = data["type"]
            if mtype == "Result":
                action = data["action"]
                if action == "JoinRoom":
                    self.on_join(data)
                elif action == "SendMessageToRoomOwner":
                    self.on_message_to_room_owner(data)
            elif mtype == "Event":
                event = data["event"]
                if event == "RoomBlobChanged":
                    self.on_room_blob_changed(data)
                elif event == "CustomerBlobChanged":
                    self.on_customer_blob_changed(data)
            else:
                logger.error("Invalid message type: %s" % data)
        else:
            logger.error("Invalid message code: %s" % msg)
    
    async def __send(self, code, args):
        args = {"name": "msg", "args": [args]}
        msg = "%s:::%s" % (code, json.dumps(args))
        logger.debug("Sending %s" % msg)
        await self.ws.send(msg)

    async def connect(self, server, id):
        self.ws = await websockets.connect("wss://%s:38203/socket.io/1/websocket/%s" % (server,id))
        await self.__recv()
    
    async def join_room(self, name):
        await self.__send(5, {
            "action": "JoinRoom",
            "appId": APPID,
            "joinType": "player",
            "name": name,
            "options": {
                "name": name,
                "roomcode": self.__room,
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()
    
    async def wait(self):
        await self.__recv()
    
    async def new_episode(self, title):
        await self.__send(5, {
            "action": "SendMessageToRoomOwner",
            "appId": APPID,
            "message": {
                "action": "new",
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()
        await self.__send(5, {
            "action": "SendMessageToRoomOwner",
            "appId": APPID,
            "message": {
                "action": "title",
                "text": title,
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()
    
    async def add_item(self, item):
        await self.__send(5, {
            "action": "SendMessageToRoomOwner",
            "appId": APPID,
            "message": {
                "action": "add",
                "text": item,
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()
    
    async def save_episode(self):
        await self.__send(5, {
            "action": "SendMessageToRoomOwner",
            "appId": APPID,
            "message": {
                "action": "save",
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()

    async def submit_episode(self):
        await self.__send(5, {
            "action": "SendMessageToRoomOwner",
            "appId": APPID,
            "message": {
                "action": "submit",
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()
    
    async def close(self):
        await self.__send(5, {
            "action": "SendMessageToRoomOwner",
            "appId": APPID,
            "message": {
                "action": "close",
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()

    async def toggle_visibility(self):
        await self.__send(5, {
            "action": "SendMessageToRoomOwner",
            "appId": APPID,
            "message": {
                "action": "toggle-visibility",
                "target": "screen",
            },
            "roomId": self.__room,
            "type": "Action",
            "userId": self.__uid,
        })
        await self.__recv()
    
    async def wait_for_episode_name(self):
        self.__got_episode_name = False
        while not self.__got_episode_name:
            await self.__recv()
        return self.__episode_name

    def on_connect(self):
        logger.info("Connect acknowledged")
    
    def on_join(self, data):
        logger.info("joined: %s" % data)

    def on_room_blob_changed(self, data):
        logger.info("Room changed: %s" % data)
    def on_customer_blob_changed(self, data):
        logger.info("Customer changed: %s" % data)
    def on_message_to_room_owner(self, data):
        logger.info("New Episode: %s" % data)


async def do_it(server, wsid, room, name, uid, title, words):
    c = Client(uid, room)
    await c.connect(server, wsid)
    await c.join_room(name)
    await c.new_episode(title)
    print("Submitting %s" % words)
    for w in words:
        await c.add_item(w)
    await c.save_episode()
    await c.submit_episode()
    await c.close()
    await c.wait_for_episode_name()

def create_wordlist(room, title, words):
    jar = requests.cookies.RequestsCookieJar()
    requests.get("https://jackbox.tv", cookies = jar)
    data = json.loads(requests.get("https://blobcast.jackboxgames.com/room/%s?userId=%s" % (room,UID), cookies = jar).text)
    if "success" in data and data["success"] == False:
        logger.error("Failed to open connection: %s" % data['error'])
        return
    logger.debug('Connection info: %s' % data)

    cur_time = int(time.time() * 1000)
    wsdata = requests.get("https://%s:38203/socket.io/1/websocket/?t=%s" % (data["server"], cur_time), cookies = jar)
    logger.debug("Obtained websocket data: %s" % wsdata.text)
    wsdata = wsdata.text.split(",")[0].split(":")[0]

    asyncio.get_event_loop().run_until_complete(
        do_it(data["server"], wsdata, room, NAME, UID, title, words)
    )
