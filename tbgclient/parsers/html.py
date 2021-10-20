import datetime, re
from html.parser import HTMLParser
import warnings

# Too many violations: not gonna attempt to comply PEP 8


class HTMLSearch(HTMLParser):
    """A tool to filter/find elements in a HTML document."""
    # *gasp* Is that JavaScript?
    text=""
    found=None
    layers=0
    result=""
    search=""
    results=[]
    multiple=False
    tag=""
 
    def __init__(self, text: str):
        self.text=text
        HTMLParser.__init__(self)
 
    def resetSettings(self):
        self.found=None
        self.layers=0
        self.result=""
        self.search=""
        self.searchIn="attrs"
        self.results=[]
        self.multiple=False
        self.tag=""
 
    def getElementByID(self, id: str):
        self.resetSettings()
        self.search=id
        self.tag="id"
        self.feed(self.text)
        return HTMLSearch(self.result)
 
    def getElementsByClass(self, klas: str):
        self.resetSettings()
        self.search=klas
        self.tag="class"
        self.multiple=True
        self.feed(self.text)
        return [HTMLSearch(x) for x in self.results]
 
    def getElementsByTagName(self, tag: str):
        self.resetSettings()
        self.search=tag
        self.searchIn="tag"
        self.multiple=True
        self.feed(self.text)
        return [HTMLSearch(x) for x in self.results]
 
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if not self.found:
            if self.searchIn == "attrs":
                if self.tag in attrs:
                    if attrs[self.tag] == self.search:
                        self.found=tag
                        self.result=""
            elif self.searchIn == "tag":
                if self.search == tag:
                    self.found=tag
                    self.result=""
            else: raise ValueError("What is "+self.searchIn)
        if self.found:
            self.result+=f"<{tag} {' '.join('%s=%s'%(x,repr(attrs[x])) for x in attrs)}>"
            if self.found==tag:
                self.layers+=1
 
    def handle_endtag(self, tag):
        if self.found:self.result+=f"</{tag}>"
        if self.found==tag: 
            self.layers-=1 
            if self.layers<=0: 
                self.found=None
                if self.multiple: self.results.append(self.result)
 
    def handle_data(self, data):
        if self.found:self.result+=data


def get_post(document, id):
    """Finds the  using HTMLParser"""
    document = HTMLSearch(document)
    if document.getElementByID("msg").text: 
        post = document.getElementByID("msg")
        return {"rawHTML": post.text, "pid": id, "tid": None, "fid": None, "user": None, "text": None, "time": None}
    topic = document.getElementsByClass("crumbs")[0].getElementsByTagName("a")[-1].text
    topic = int(re.sub(r"""<a href=['"]viewtopic\.php\?id=(\d*)['"]>(?:.*)</a>""",r"\1",topic))
    forum = document.getElementsByClass("crumbs")[0].getElementsByTagName("a")[-2].text
    forum = int(re.sub(r"""<a href=['"]viewforum\.php\?id=(\d*)['"]>(?:.*)</a>""",r"\1",forum))
    post = document.getElementByID(f"p{id}")
    text, time = (None, None)
    user = post.getElementsByTagName("dl")
    if user: 
        user = user[0].getElementsByTagName("dt")[0].text
        user = re.sub(r"<dt *><strong *>(.*)</strong></dt>",r"\1",user)
        text = "".join(x.text for x in post.getElementsByClass("postmsg")[0].getElementsByTagName("p"))
        time = post.getElementsByTagName("a")[0].text
        time = re.search(r">(.*)<",time).group(1).split(" ")
        time[1] = datetime.datetime.strptime(time[1],"\u2009%H:%M:%S").time()
        if time[0] == "Today": time = datetime.datetime.combine(datetime.datetime.now().date(),time[1])
        elif time[0] == "Yesterday": 
            time = datetime.datetime.combine(datetime.datetime.now().date(),time[1])
            time += datetime.timedelta(days=-1)
        else: time = datetime.datetime.combine(datetime.datetime.strptime(time[0],"%Y-%b-%d").date(),time[1])
        time = str(time)
    else: 
        warnings.warn("Cannot find post ID in document",RuntimeWarning)
        user=None
    return {"rawHTML": post.text, "pid": id, "tid": topic, "fid": forum, "user": user, "text": text, "time": time}


def get_element_by_id(document, id):
    return HTMLSearch(document).getElementByID(id).text


def get_elements_by_class(document, klas):
    return [x.text for x in HTMLSearch(document).getElementsByClass(id)]


def get_elements_by_tag_name(document, tag):
    return [x.text for x in HTMLSearch(document).getElementsByTagName(id)]


__all__ = dir(globals())
