"""Handles low-level API calls."""

import requests
from . import TBGException

silent = False


def post_post(session, post, tid):
    req = session.post(f"https://tbgforums.com/forums/post.php?tid={tid}", {"req_message": post, "form_sent": 1})
    if req.status_code > 400 and not silent:
        raise TBGException.RequestException(f"Got {req.status_code} at POST")
    return session, req


def get_post(session, pid):
    req = session.get(f"https://tbgforums.com/forums/viewtopic.php?pid={pid}")
    if req.status_code > 400 and not silent:
        raise TBGException.RequestException(f"Got {req.status_code} at GET")
    return session, req


def login(session, user, password):
    req = session.post(f"https://tbgforums.com/forums/login.php?action=in",
                       {"req_username": user, "req_password": password, "form_sent": "1", "login": "Login"}
                       )
    if req.status_code >= 400:
        raise TBGException.RequestException(f"Got {req.status_code} at login")
    return session, req


def get_user(session, uid):
    req = session.get(f"https://tbgforums.com/forums/profile.php?id={uid}")
    if req.status_code > 400 and not silent:
        raise TBGException.RequestException(f"Got {req.status_code} at GET")
    return session, req
