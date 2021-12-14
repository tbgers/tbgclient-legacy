"""Handles low-level API calls."""

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


def get_topic(session, tid, page=1):
    req = session.get(f"https://tbgforums.com/forums/viewtopic.php?id={tid}&p={page}")
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


def search(session, query, author="", search_in=0, forums=[], sort=0, direction=-1, show_as="topics"):
    direction = "DESC" if direction < -1 else "ASC"
    req = session.get(
        f"https://tbgforums.com/forums/search.php?action=search&" +
        f"keywords={query}&author={author}&search_in={search_in}&sort_by={sort}&" +
        "&".join(f"forums[]={x}" for x in forums) + 
        f"&sort_dir={direction}&show_as={show_as}&search=Submit",
        timeout=None)
    if req.status_code > 400 and not silent:
        raise TBGException.RequestException(f"Got {req.status_code} at GET")
    return session, req

def get_message(session, channel, lastID=0, getInfo: tuple = tuple()):
    req = session.get(
        "https://tbgforums.com/forums/chat/?ajax=true&" +
        f"lastID={lastID}&" +
        f"getInfos={','.join(getInfo)}&" + 
        f"channelID={channel}"
    )
    if req.status_code > 400 and not silent:
        raise TBGException.RequestException(f"Got {req.status_code} at GET")
    return session, req

def post_message(session, message, lastID=0):
    req = session.post(
        "https://tbgforums.com/forums/chat/?ajax=true",
        {"lastID": str(lastID), "text": message}
    )
    if req.status_code > 400 and not silent:
        raise TBGException.RequestException(f"Got {req.status_code} at POST")
    return session, req
