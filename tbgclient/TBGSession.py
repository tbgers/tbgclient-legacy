"""Manages sessions."""

import requests, re, warnings
from tbgclient import api, TBGException, Post, Flags


def _check_error(req, parser):
    """Checks for errors on the document."""
    # HACK: Using regex to find list, tbgclient.parsers cannot parse document correctly
    error = re.findall(r'<div class="inbox error-info">(.+?)</div>', req.text, re.DOTALL)
    if not error: return None
    error = re.findall(r'<ul class="error-list">(.+?)</ul>', error[0], re.DOTALL)
    error = parser.get_elements_by_tag_name(error[0], "strong")
    error = [re.sub(r"<\/?[^>]+(>|$)", "", x) for x in error]
    print(error)
    return error


class TBGSession:

    session = requests.Session()
    user = ""
    password = ""

    def __init__(self, user: str, password: str, parser=None, flags=set()):
        """Initiates the class."""
        if parser is None:
            from tbgclient import parsers
            self.parser = parsers.default
        self.user = user
        self.password = password
        if Flags.NO_LOGIN not in flags:
            req = self.login()

    def get(self, pid: int):
        """Gets a post."""
        self.session, req = api.get_post(self.session, pid)
        return Post(**self.parser.get_post(req.text, pid))

    def post(self, post: str, tid: int):
        """Posts a post."""
        if type(post) == Post:
            post = post.to_bbcode()
        self.session, req = api.post_post(self.session, post, tid)
        error = _check_error(req, self.parser)
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
            warnings.warn(f"Login failed {tuple(match)}", TBGException.TBGWarning)
        return req
