"""An implementation of posts."""
from tbgclient import Flags


class Post:
    """An object that defines a post.

    Parameters
    ----------
    rawHTML: str
        The raw HTML of
    pID: int
        The post's post ID number
    tID: int
        The topic ID number this post lies on.
    fID: int
        The forum ID number this post lies on.
    uID: int
        The poster's user ID number.
    user: str
        The poster's username.
    text: str
        The contents of the post.
    """
    rawHTML = ""
    pID = None
    tID = None
    fID = None
    uID = None
    user = None
    text = None
    time = None

    def __init__(self, **data):
        self.__dict__.update(data)
        if Flags.NO_INIT not in self.flags:
            self.update()

    def to_bbcode(self):
        # TODO: Implement HTML to BBCode conversion
        raise NotImplementedError

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Post(user={self.user},time={self.time})"

    def update(self):
        match = re.match('<a href="profile.php?id=(\d+)">', self.rawHTML)
        if match:
            
