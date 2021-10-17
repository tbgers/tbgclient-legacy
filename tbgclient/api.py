"""Handles low-level API calls."""

import requests
from tbgclient import TBGException

silent = False

def post_post(session, post, tID):
    req = session.post(f"https://tbgforums.com/forums/post.php?tid={tID}", {"req_message": post, "form_sent": 1})
    if req.status_code > 400 and not silent: raise TBGException.RequestException(f"Got {req.status_code} at POST")
    return session, req
    
def get_post(session, pID):
    req = session.get(f"https://tbgforums.com/forums/viewtopic.php?pid={pID}")
    if req.status_code > 400 and not silent: raise TBGException.RequestException(f"Got {req.status_code} at GET")
    return session, req
    
def login(session, user, password):
    req = session.post(f"https://tbgforums.com/forums/login.php?action=in", {"req_username": user,"req_password": password, "form_sent": "1", "login": "Login" })
    if req.status_code >= 400: raise TBGException.RequestException(f"Got {req.status_code} at login")
    return session, req