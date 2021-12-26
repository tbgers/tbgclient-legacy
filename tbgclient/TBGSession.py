"""An implementation of a TBG session."""

import re
import requests

from . import api
from .Flags import Flags
from .Post import Post
from .TBGException import *
from .Topic import Topic
from .User import User
from .ChatConnection import ChatConnection
from . import parsers


class TBGSession:
    """An object that defines a TBG session.

    This class provides a client session while also functions as a wrapper 
    of tbgclient.api.

    Parameters
    ----------
    user: str
        Username of the TBG account. If left blank, the Flags.NO_LOGIN 
        flag will be set.
    password: str
        Password of the TBG account. If left blank, the Flags.NO_LOGIN 
        flag will be set.
    flags: tbgclient.Flags
        Flags for the session. See tbgclient.Flags for more information.

    Variables
    ---------
    session: request.Session()
        The client session.
    uID: int
        The user ID of the session. This will be updated if update() is
        called.

    Methods
    -------

    """
    session = requests.Session()
    user = ""
    password = ""
    uID = None
    flags: Flags = Flags.NONE

    def __init__(self, user: str = None, password: str = None, flags: Flags = Flags.NONE):
        """Initiates the class."""
        self.flags = flags
        if password is None or user is None:
            # enter guest mode
            self.flags |= Flags.NO_LOGIN
        self.user = user
        self.password = password
        if Flags.NO_LOGIN not in self.flags:
            req = self.login()
        if Flags.MULTI_USER in self.flags:
            self.session = api.SessionMultiple()

    def __repr__(self):
        return f"TBGSession(user={repr(self.user)},password={repr(self.password)},flags={repr(self.flags)})"

    def get_post(self, pid: int):
        """Gets a post."""
        self.session, req = api.get_post(self.session, pid)
        if Flags.RAW_DATA not in self.flags:
            result = Post(**parsers.default.get_post(req.text, pid), flags=self.flags, session=self)
            if Flags.NO_INIT not in self.flags:
                result.update(full=False)
            return result
        else:
            return parsers.default.get_post(req.text, pid)
            
     def delete_post(self, pid: int):
        """Deletes a post."""
        self.session, req = api.delete_post(self.session, pid)

    def get_topic(self, tid: int):
        """Gets a topic."""
        self.session, req = api.get_topic(self.session, tid)
        if Flags.RAW_DATA not in self.flags:
            result = Topic(**parsers.default.get_page(req.text), flags=self.flags, session=self)
            if Flags.NO_INIT not in self.flags:
                result.update()
            return result
        else:
            return parsers.default.get_post(req.text, tid)

    def get_user(self, uID: int):
        """Gets a user."""
        self.session, req = api.get_user(self.session, uID)
        if Flags.RAW_DATA not in self.flags:
            return User(**parsers.default.get_user(req.text), flags=self.flags)
        else:
            return parsers.default.get_user(req.text)

    def create_chat_connection(self, channel: int, **kwargs):
        """Creates a chat connection.

        This is identical to ChatConnection(**kwargs, session=self).connect(channel).
        """
        connect = ChatConnection(**kwargs, session=self)
        return connect.connect(channel)

    def post_reply(self, post: str, tid: int):
        """Posts a post.

        This is identical to self.get_topic(tid).post_reply(post).
        """
        topic = self.get_topic(tid)
        return topic.post_reply(post)

    def login(self):
        """Logs into the TBGs."""
        self.session, req = api.login(self.session, self.user, self.password)
        # verify if you're logged in, for some reason the forums will send 200 even if your user/pass is invalid
        match = re.findall('<p class="conl">(.+)</p>', req.text)
        if len(match) != 0:
            raise CredentialsException(
                f"Login failed, you have a faulty credential information. {tuple(match)}"
            )
        return req

    def to_user(self):
        """Casts TBGSession to User."""
        if self.uID is None:
            # user id is not defined
            req = self.session.get("https://tbgforums.com/forums/index.php")
            self.uID = parsers.default.get_element_by_id(req.text, "navprofile")
            self.uID = int(re.findall(r'profile\.php\?id=(\d*)', self.uID)[0])
        self.get_user(self.uID)


__all__ = ["TBGSession"]
