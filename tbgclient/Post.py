"""An implementation of posts."""
from . import parsers, api
from .Flags import Flags
from .User import User

import re


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
    """
    rawHTML = ""
    pID: int = None
    tID: int = None
    fID: int = None
    uID: int = None
    user = None
    text: str = None
    time: str = None
    flags: Flags = Flags.NONE
    session = None

    def __init__(self, **data):
        self.__dict__.update(data)

    def to_bbcode(self):
        # TODO: Implement HTML to BBCode conversion
        raise NotImplementedError

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Post(user={repr(self.user)},time={repr(self.time)},text={repr(self.text)})"

    def update(self):
        if Flags.NO_INIT in self.flags:
            return
        match = re.match(r'<a href=["\']profile\.php\?id=(\d+)["\']>', self.user)
        if match:
            self.uID = int(match.group(1))
            self.session, req = api.get_user(self.session.session, self.uID)
            if Flags.RAW_DATA not in self.flags:
                self.user = User(uID=self.uID, **parsers.default.get_user(req.text), flags=self.flags)
            else:
                self.user = parsers.default.get_user(req.text)

