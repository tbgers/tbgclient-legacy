"""An implementation of posts."""

class Post:
    rawHTML = ""
    pID = None
    tID = None
    fID = None
    user = None
    text = None
    time = None
    def __init__(self, **data):
        self.__dict__.update(data)
    def to_BBCode(self):
        # TODO: Implement HTML to BBCode conversion
        raise NotImplementedError
    def __str__(self):
        return self.text
    def __repr__(self):
        return f"Post(user={self.user},time={self.time})"