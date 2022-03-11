"""An implementation of forums."""
# this could be improved by polymorphism
# but i decided not to implement that for now
from . import parsers, api
from .Flags import Flags
from .TBGException import *
from .Topic import Topic
import re


def _check_error(req, parser):
    """Checks for errors on the document."""
    # HACK: Using regex to find list, tbgclient.parsers cannot parse document correctly
    error = re.findall(r'<div class="inbox error-info">(.+?)</div>', req.text, re.DOTALL)
    if not error:
        return None
    error = re.findall(r'<ul class="error-list">(.+?)</ul>', error[0], re.DOTALL)
    error = parser.get_elements_by_tag_name(error[0], "strong")
    error = [re.sub(r"</?[^>]+(>|$)", "", x) for x in error]
    return error


class Forum:
    """An object that defines a forum or any collection of topics.

    Variables
    ---------
    fID: int
        The forum ID of this forum.
    title: str
        The title of forum.
    pages: int
        The page count of this forum.
    flags: tbgclient.Flags
        Flags for the topic. See tbgclient.Flags for more information.
    views: int
        The amount of views this forum has. Currently unused.
    lastPost: int
        The last post of this forum. Currently unused.
    """
    fID: int
    title: str
    pages: int
    flags: Flags = Flags.NONE
    views: int
    lastPost: int
    _pageSize: int = 0
    _pageCache: dict
    posts: list

    def __init__(self, **data):
        self.__dict__.update(data)
        if "topics" in data:
            self._pageSize = len(self.topics)
            del self.topics
        self._pageCache = {}

    def __repr__(self):
        return f"Forum(fID={repr(self.fID)},title={repr(self.title)}," +\
               f"pages={repr(self.pages)},session={repr(self.session)})"

    def update(self, full=True):
        if full:
            self.session.session, req = api.get_forum(self.session.session, self.fID)
            self.__init__(**parsers.default.get_forum_page(req.text))

    def post_topic(self, post):
        """Posts a topic."""
        # TODO: Implement topic posting
        return NotImplemented

    def get_page(self, page):
        """Get posts on a single page."""
        if self.session is None:
            raise RequestException("Session is missing")
        if page <= 0:
            raise IndexError("Page index out of range")
        if page > self.pages:
            raise IndexError("Page index out of range")
        if page in self._pageCache:
            pageData = self._pageCache[page]
        else:
            self.session.session, req = api.get_forum(self.session.session, self.fID, page)
            pageData = parsers.default.get_forum_page(req.text)["topics"]
            self._pageCache[page] = pageData

        result = []
        for x in pageData:
            if Flags.RAW_DATA not in self.flags:
                topic = Topic(**x, session=self.session)
                topic.fID=self.fID
                if Flags.NO_INIT not in self.flags:
                    topic.update()
                result.append(topic)
            else:
                topic = x
                topic["fID"]=self.fID
                result.append(topic)
        return result

    def get_post(self, pNum):
        """Get post on an index."""
        if pNum <= 0:
            raise IndexError("Page index out of range")
        page, post = divmod(pNum - 1, self._pageSize)
        if page >= self.pages:
            raise IndexError("Page index out of range")
        posts = self.get_page(page + 1)
        if post >= len(posts):
            raise IndexError("Page index out of range")
        return posts[post]

    def __getitem__(self, pNum):
        return self.get_post(pNum + 1)
