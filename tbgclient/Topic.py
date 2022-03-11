"""An implementation of topics."""
from . import parsers, api
from .Flags import Flags
from .TBGException import *
from .Post import Post
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


class Topic:
    """An object that defines a topic or any collection of posts.

    Variables
    ---------
    tID: int
        The topic ID of topic.
    fID: int
        The forum ID this topic sits.
    title: str
        The title of topic.
    pages: int
        The page count of topic.
    flags: tbgclient.Flags
        Flags for the topic. See tbgclient.Flags for more information.
    views: int
        The amount of views this topic has. Only gets filled when this is 
        made on tbgclient.Forum.
    lastPost: int
        The last post of this topic. Only gets filled when this is made on
        tbgclient.Forum.
    """
    tID: int
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
        if "posts" in data:
            self._pageSize = len(self.posts)
            del self.posts
        self._pageCache = {}

    def __repr__(self):
        return f"Topic(tID={repr(self.tID)},title={repr(self.title)}," +\
               f"pages={repr(self.pages)},session={repr(self.session)})"

    def update(self, full=True):
        if full:
            self.session.session, req = api.get_topic(self.session.session, self.tID)
            self.__init__(**parsers.default.get_page(req.text))

    def post_reply(self, post):
        """Posts a post."""
        if self.session is None:
            raise RequestException("Session is missing")
        if type(post) == Post:
            post = post.to_bbcode()
        self.session.session, req = api.post_post(self.session.session, post, self.tID)
        error = _check_error(req, parsers.default)
        if error:
            raise TBGException(
                "The following errors need to be corrected before the message can be posted:\n" +
                "\n".join(f"- {x}" for x in error)
            )
        return req

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
            self.session.session, req = api.get_topic(self.session.session, self.tID, page)
            if page != self.pages and self._pageSize == 0:
                self._pageSize = len(self.posts)
            pageData = parsers.default.get_page(req.text)["posts"]
            self._pageCache[page] = pageData
        
        posts = [parsers.default.get_post(x) for x in pageData]
        result = []
        for x in posts:
            if Flags.RAW_DATA not in self.flags:
                post = Post(**x, session=self.session)
                post.tID=self.tID
                post.fID=self.fID
                if Flags.NO_INIT not in self.flags:
                    post.update()
                result.append(post)
            else: 
                post = x
                post["tID"]=self.tID
                post["fID"]=self.fID
                result.append(post)
        return result

    def get_post(self, pNum):
        """Get post on an index."""
        if pNum <= 0:
            raise IndexError("Post index out of range")
        page, post = divmod(pNum - 1, self._pageSize)
        if page >= self.pages:
            raise IndexError("Post index out of range")
        posts = self.get_page(page + 1)
        if post >= len(posts):
            raise IndexError("Post index out of range")
        return posts[post]
        
    def __getitem__(self, pNum):
        return self.get_post(pNum + 1)

