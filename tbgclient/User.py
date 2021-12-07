"""An implementation of users other than yourself."""
# TODO: Someone else can add the parts that makes these. (in TBGSession.py, and probably in parsers/html.py and parsers/lxml.py)


class User:
    uID = None
    username = ""
    title = None
    location = None
    website = None
    signature = ""
    realname = None

    def __init__(self, **data):
        self.__dict__.update(data)

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"User(username={self.username},uID={self.uID})"
