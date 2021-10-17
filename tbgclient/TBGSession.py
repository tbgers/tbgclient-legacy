"""Manages sessions."""

import requests, importlib, re, warnings
from enum import Enum
from tbgclient import api, TBGException, Post

class TBGSession:
    
    session = requests.Session()
    user = ""
    password = ""
    def __init__(self, user: str, password: str, parser=None, flags=set()):
        """Initiates the class."""
        if parser == None:
            from tbgclient import parsers
            self.parser = parsers.default
        self.user = user
        self.password = password
        req = self.login()
    def get(self, pID: int):
        """Gets a post."""
        self.session, req = api.get_post(self.session, pID)
        return Post(**self.parser.get_post(req.text, pID))
    def post(self, post: str, tID: int):
        """Posts a post."""
        if type(post) == Post:
            post = post.to_BBCode()
        self.session, req = api.post_post(self.session, post, tID)
        error = self._checkError(req, self.parser)
        if error:
            raise TBGException.TBGException("The following errors need to be corrected before the message can be posted:\n"+
                  "\n".join(f"- {x}" for x in error)
            )
        return req
    def _checkError(self, req, parser):
        """Checks for errors on the document."""
        # HACK: Using regex to find list, tbgclient.parsers cannot parse document correctly 
        error = re.findall(r'<div class="inbox error-info">(.+?)</div>',req.text,re.DOTALL) 
        if not error: return None
        error = re.findall(r'<ul class="error-list">(.+?)</ul>',error[0],re.DOTALL)
        error = parser.get_elements_by_tag_name(error[0], "strong")
        error = [re.sub(r"<\/?[^>]+(>|$)", "", x) for x in error]
        print(error)
        return error
    def login(self):
        """Logs into the TBGs."""
        self.session, req = api.login(self.session, self.user, self.password)
        # verify if you're logged in, for some reason the forums will send 200 even if your user/pass is invalid
        match = re.findall('<p class="conl">(.+)</p>', req.text)
        if len(match) != 0: 
            warnings.warn(f"Login failed {tuple(match)}", TBGException.TBGWarning)
        return req