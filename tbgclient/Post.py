class Post:
    rawHTML = ""
    pID = None
    tID = None
    fID = None
    user = None
    text = None
    time = None
    def __init__(self, data):
        self.__dict__.update(data)