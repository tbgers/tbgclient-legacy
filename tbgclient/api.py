"""Handles low-level API calls."""

import requests

def post_post(session, post, tID):
    req = session.post(f"https://tbgforums.com/forums/post.php?tid={tID}", data={"req_message": post, "form_sent": 1})
    if req.status_code > 400: raise TBGException.RequestException(req.status_code)
    return session, req
    
def get_post(session, pID):
    req = session.get(f"https://tbgforums.com/forums/viewtopic.php?pid={pID}")
    if req.status_code > 400: raise TBGException.RequestException(req.status_code)
    return session, req
    
def login(session, user, password):
    req = session.post("https://tbgforums.com/forums/login.php?action=in", data={"req_username": user, "req_password": password, "form_sent": 1, "login": "Login"})
    if req.status_code > 400: raise TBGException.RequestException(req.status_code)
    return session, req