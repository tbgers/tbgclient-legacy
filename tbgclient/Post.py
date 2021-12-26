"""An implementation of posts."""
from . import parsers, api
from .Flags import Flags
from .User import User
from .TBGException import *
from enum import Enum, auto

import re


class PostType(Enum):
    """Defines types of posts."""
    NORMAL = auto()
    CHAT = auto()


class Post:
    """An object that defines a post.

    Parameters
    ----------
    rawHTML: str
        The raw HTML of the post.
    pID: int
        The post's post ID number
    tID: int
        The topic ID number this post lies on.
    fID: int
        The forum ID number this post lies on.
    uID: int
        The poster's user ID number.
    user: str, tbgclient.User
        The poster of the post.
    text: str
        The contents of the post.
    time: str
        The time when this post is posted.
    postType: tbgclient.Post.PostType
        The post type of this post.
    flags: tbgclient.Flags
        Flags for this post. See tbgclient.Flags for more information.
    """
    rawHTML: str = ""
    pID: int = None
    tID: int = None
    fID: int = None
    uID: int = None
    user = None
    text: str = None
    time: str = None
    flags: Flags = Flags.NONE
    postType: PostType = PostType.NORMAL
    session = None

    def __init__(self, **data):
        self.__dict__.update(data)

    def to_bbcode(self):
        # TODO: Implement HTML to BBCode conversion
        raise NotImplementedError

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Post(user={repr(self.user)},pID={repr(self.pID)},text={repr(self.text)},session={repr(self.session)})"

    def update(self, full=True):
        if self.session is None:
            raise RequestException("Session is missing")
        if full:
            self.session.session, req = api.get_post(self.session.session, self.pID)
            self.__init__(**parsers.default.get_post(req.text, self.pID))
        if type(self.user) is dict:
            self.user = User(**self.user, session=self.session, flags=self.flags)
        else:
            match = re.match(r'<a href=["\']profile\.php\?id=(\d+)["\']>', self.user)
            if match:
                self.uID = int(match.group(1))
                self.session.session, req = api.get_user(self.session.session, self.uID)
                if Flags.RAW_DATA not in self.flags:
                    self.user = User(uID=self.uID, **parsers.default.get_user(req.text), flags=self.flags)
                else:
                    self.user = parsers.default.get_user(req.text)

