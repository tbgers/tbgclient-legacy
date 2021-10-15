"""Manages sessions."""
import requests, importlib
from tbgclient import api, TBGException
from tbgclient.TBGException import *

class TBGSession:
    session = requests.Session
    user = ""
    password = ""
    def __init__(self, user, password, parser=None):
        if parser == None:
            from tbgclient import parsers
            self. parser = parsers.lxml
        self.user = user
        self.password = password
        self.login()
    def get_post(self, pID):
        """Gets a post."""
        self.session, req = api.get_post(pID)
        return parser.get_post(req.text, pID)
    def login(self):
        """Logs into the TBGs."""
        self.session, req = api.login(session, self.user, self.password)