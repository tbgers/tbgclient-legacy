"""An implementation of searches."""
import re
import requests
from . import api
from .Topic import Topic


class Search: # TODO: Implement Search
    """An object that defines a search session.
    
    Variables
    ---------
    sID: int
        The search ID of this search session.
    """
    pass
    sID: int
    _postCache: dict
    
    def __init__(self, **data):
        posts = data["posts"]
        self.__dict__.update(data)
        self._postCache = {} # reset cache
        
    def update(self, full=True):
        if full:
            self.session.session, result = api.search(self.session.session, "test", show_as="posts")
            self.__init__(**parsers.default.get_page(result.text))
            self.sID = int(re.search("(\d+)", result.url)[1])
        
    def get_page():
        """Get a page of posts."""
        pass
