"""Manages sessions."""

import re
import requests

from . import api
from .Flags import Flags
from .Post import Post
from .TBGException import *
from .User import User
from . import parsers


def _check_error(req, parser):
    """Checks for errors on the document."""
    # HACK: Using regex to find list, tbgclient.parsers cannot parse document correctly
    error = re.findall(r'<div class="inbox error-info">(.+?)</div>', req.text, re.DOTALL)
    if not error: return None
    error = re.findall(r'<ul class="error-list">(.+?)</ul>', error[0], re.DOTALL)
    error = parser.get_elements_by_tag_name(error[0], "strong")
    error = [re.sub(r"</?[^>]+(>|$)", "", x) for x in error]
    print(error)
    return error


class TBGSession:
    """An object that defines a TBG session.

    This class provides a client session while also functions as a
    wrapper of tbgclient.api.

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
        The user ID of the session.
    """
    session = requests.Session()
    user = ""
    password = ""
    uID = None
    flags = Flags.NONE

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

    def get(self, pid: int):
        """Gets a post."""
        self.session, req = api.get_post(self.session, pid)
        if Flags.RAW_DATA not in self.flags:
            result = Post(**parsers.default.get_post(req.text, pid), flags=self.flags, session=self)
            result.update()
            return result
        else:
            return parsers.default.get_post(req.text, pid)

    def post(self, post: str, tid: int):
        """Posts a post."""
        if type(post) == Post:
            post = post.to_bbcode()
        self.session, req = api.post_post(self.session, post, tid)
        error = _check_error(req, parsers.default)
        if error:
            raise TBGException.TBGException(
                "The following errors need to be corrected before the message can be posted:\n" +
                "\n".join(f"- {x}" for x in error)
            )
        return req

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
            self.uID = int(re.findall(r'href="profile\.php\?id=(.*)"')[0])
        self.session, req = api.get_user(self.session, self.uID)
        if Flags.RAW_DATA not in self.flags:
            return User(**parsers.default.get_user(req.text), flags=self.flags)
        else:
            return parsers.default.get_user(req.text)


__all__ = ["TBGSession"]