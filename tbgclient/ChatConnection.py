"""An implementation of a chat connection."""
import threading
import warnings
import time
import asyncio

from . import api
from .Post import Post, PostType
from .User import User
from .Flags import Flags
from .TBGException import *
from . import parsers


class ChatConnection:
    """Connects to the chat.
    
    This connects to https://tbgforums.com/forums/chat.php, allowing you to
    get and post messages there.

    Variables
    ---------
    refreshRate: int
        Minumum delay time every GETs.
    channel: int
        Current channel of the connection.
    channelName: str
        Current channel name of the connection.
    flags: tbgclient.Flags
        Flags for the connection. See tbgclient.Flags for more information.
    lastID: int
        The last post ID fetched.
    users: dict
        A list of online users.
    """
    refreshRate: int = 1
    lastID: int = 0
    session = None
    channel: int = 0
    channelName: str = ""
    flags: Flags = Flags.NONE
    loop: threading.Thread
    tasks = None
    isAsync: bool = False
    users: dict = None
    connected: bool = False

    def __init__(self,  **data):
        self.__dict__.update(data)
        self.loop = threading.Thread(name='post', target=self.main_loop, args=tuple(), daemon=True)
        
    def connect(self, channel):
        """Connects to a channel."""
        self.channel = channel
        if not self.loop.is_alive(): self.loop.start()
        self.on_login(self.session)
        return self

    def main_loop(self):
        """The main loop."""
        async def do_nothing():
            """Does nothing."""
            pass
        
        self.connected = True
        self.isAsync = asyncio.iscoroutinefunction(self.on_message)
        if self.isAsync:
            self.tasks = asyncio.new_event_loop()
            asyncio.set_event_loop(self.tasks)
        else:
            self.tasks = []

        try:
            first = True
            while True:
                if not self.connected:
                    return
                self.session.session, req = api.get_message(self.session.session, self.channel, 
                                                            self.lastID, ["channelName"])
                xml = parsers.default.get_message(req.text)
                xml["users"] = {k: [User(**x, flags=self.flags, session=self.session) for x in v]
                                for k, v in xml["users"].items()}
                xml["messages"] = [Post(**x, flags=self.flags, session=self.session, postType=PostType.CHAT) 
                                   for x in xml["messages"]]
                self.channelName = xml["info"]["channelName"]
                self.users = xml["users"]

                if len(xml["messages"]) != 0: 
                    self.lastID = xml["messages"][-1].pID
                
                if not first:
                    if self.isAsync:
                        # Make and execute new tasks
                        for x in xml["messages"]:
                            self.tasks.create_task(self.on_message(x))
                        self.tasks.run_until_complete(do_nothing())
                    else:
                        # Scrub finished threads
                        finished = []
                        for i, x in enumerate(self.tasks):
                            if not x.is_alive():
                                finished.append(i)
                        self.tasks = [x for i, x in enumerate(self.tasks) if i not in finished]

                        # Make and execute new threads
                        for x in xml["messages"]:
                            self.tasks.append(threading.Thread(name=f"p{x.pID}", target=self.on_message,
                                                               sargs=(x,), daemon=True))
                        
                        for i, x in enumerate(self.tasks):
                            if not x.is_alive():
                                self.tasks[i].start()
                first = False

                time.sleep(self.refreshRate)
        except Exception as e:
            self.on_error(e)
            raise

    def set_event(self, etype):
        """Decorates a function to be used as events."""
        if etype not in ["on_error", "on_message", "on_login"]:
            raise ValueError(f"Invalid event type: {etype}")
        f = None
        def wrapper(func):
            nonlocal f
            self.__setattr__(etype, func)
        return f

    def send_message(self, msg):
        if type(msg) is Post:
            if msg.postType != PostType.CHAT:
                warnings.warn("Post type is not PostType.CHAT", TBGWarning)
            msg = msg.post
        else:
            msg = str(msg)
        self.session.session, req = api.post_message(self.session.session, msg)
        xml = parsers.default.get_message(req.text)
        xml["messages"] = [Post(**x, flags=self.flags, session=self.session, postType=PostType.CHAT) 
                           for x in xml["messages"]]
        if len(xml["messages"]) != 0: 
            self.lastID = xml["messages"][-1].pID
        else: 
            self.lastID += 1
        return req

    def disconnect(self):
        self.connected = False

    # These are meant to be user-defined functions.
    def on_error(self, e: Exception):
        """Called when self.main_loop() throws an error."""
        pass

    async def on_message(self, message):
        """Called every message read.

        Overrides isAsync if this function is asynchronous."""
        pass

    def on_login(self, user):
        """Called every login."""
        pass
    

    





