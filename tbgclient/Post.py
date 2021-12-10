"""An implementation of posts."""
from tbgclient import parsers, api
from tbgclient.Flags import Flags
from tbgclient.User import User
import re
import requests


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
        The poster's username, or
    text: str
        The contents of the post.
    time: str
        The time when this post is posted.
    """
    rawHTML = ""
    pID = None
    tID = None
    fID = None
    uID = None
    user = None
    text = None
    time = None
    flags = Flags.NONE
    session = requests.Session()

    def __init__(self, **data):
        self.__dict__.update(data)

    def to_bbcode(self):
        # TODO: Implement HTML to BBCode conversion
        raise NotImplementedError

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Post(user={repr(self.user)},time={repr(self.time)})"

    def update(self, session):
        if Flags.NO_INIT in self.flags:
            return
        match = re.match(r'<a href="profile\.php\?id=(\d+)">', self.user)
        print(match, self.user)
        if match:
            self.uID = int(match.group(1))
            self.session, req = api.get_user(session.session, self.uID)
            print(req.text)
            if Flags.RAW_DATA not in self.flags:
                self.user = User(**parsers.default.get_user(req.text), flags=self.flags)
            else:
                self.user = parsers.default.get_user(req.text)

