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
    disable=False
 
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

    def getChildNodes(self):
        self.resetSettings()
        self.searchIn="child"
        self.multiple=True
        self.disable=True
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
            elif self.searchIn == "child":
                if self.disable: self.disable=False
                else:
                    self.found = tag
                    self.result = ""
            else: raise ValueError("What is "+self.searchIn)
        if self.found:
            self.result+=f"<{tag}{''.join(' %s=%s'%(x,repr(attrs[x])) for x in attrs)}>"
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


def get_post(document, pid=None):
    """Finds post using HTMLParser"""
    document = HTMLSearch(document)
    if pid is not None:
        if document.getElementByID("msg").text:
            post = document.getElementByID("msg")
            return {"rawHTML": post.text, "pid": pid, "tid": None, "fid": None, "user": None, "text": None, "time": None}
        topic = document.getElementsByClass("crumbs")[0].getElementsByTagName("a")[-1].text
        topic = int(re.sub(r"""<a href=['"]viewtopic\.php\?id=(\d*)['"]>(?:.*)</a>""",r"\1",topic))
        forum = document.getElementsByClass("crumbs")[0].getElementsByTagName("a")[-2].text
        forum = int(re.sub(r"""<a href=['"]viewforum\.php\?id=(\d*)['"]>(?:.*)</a>""",r"\1",forum))
        post = document.getElementByID(f"p{pid}")
    else:
        post = document
        pid = int(re.search(r"p(\d+)", document.text).group(1))
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
    return {"rawHTML": post.text, "pID": pid, "tID": topic, "fID": forum, "user": user, "text": text, "time": time}


def get_element_by_id(document, id):
    return HTMLSearch(document).getElementByID(id).text


def get_elements_by_class(document, klas):
    return [x.text for x in HTMLSearch(document).getElementsByClass(id)]


def get_elements_by_tag_name(document, tag):
    return [x.text for x in HTMLSearch(document).getElementsByTagName(id)]


def get_user(document):
    a = HTMLSearch(document)
    if a.getElementsByClass("blockmenu"): 
        raise NotImplementedError
    a = a.getElementsByTagName("fieldset")
    a = [x.getElementsByTagName("dl")[0].text for x in a]
    k = [[y.group(2) for y in re.finditer(r"<(dt) ?.*?>(.*?)</\1>", x)] for x in a]
    v = [[y.group(2) for y in re.finditer(r"<(dd) ?.*?>(.*?)</\1>", x)] for x in a]
    a = [{p: q for p, q in zip(x, y)} for x, y in zip(k, v)]
    a = {k: v for x in a for k, v in x.items()}

    r = {}
    s = {}
    if "Username" in a:
        r["username"] = a["Username"]
    if "Title" in a:
        r["title"] = a["Title"]
    if "Location" in a:
        r["location"] = a["Location"]
    if "Website" in a:
        r["website"] = re.findall(">(.*)<", HTMLSearch(a["Website"]).getElementsByTagName("a")[0].text)[0]
    if "Signature" in a:
        r["signature"] = re.findall(">(.*)<", a["Signature"])[0]
    if "Real name" in a:
        r["realname"] = a["Real name"]
    if "Posts" in a:
        r["postcount"] = int(a["Posts"].split(" - ")[0].replace(",", ""))
    if "Registered" in a:
        r["registered"] = datetime.datetime.strptime(a["Registered"], "%Y-%b-%d").date()

    if "Jabber" in a:
        s = a["Jabber"]
    if "ICQ" in a:
        s = a["ICQ"]
    if "MSN Messenger" in a:
        s = a["MSN Messenger"]
    if "AOL IM" in a:
        s = a["AOL IM"]
    if "Yahoo! Messenger" in a:
        s = a["Yahoo! Messenger"]
    r["social"] = s
    return r


def get_page(document):
    """Get page data using HTMLParser."""
    document = HTMLSearch(document)
    raw = document.getElementByID("brdmain")
    topic, name, forum, pages, posts = (None,) * 5  # le init
    if document.getElementByID("msg").text == "":
        topic = document.getElementsByClass("crumbs")[0].getElementsByTagName("a")[-1].text
        topic, name = re.findall(r"""<a href=['"]viewtopic\.php\?id=(\d*)['"]>(.*)</a>""",topic)[0]
        topic = int(topic)
        name = re.search(r">(.+)<", name).group(1)
        forum = document.getElementsByClass("crumbs")[0].getElementsByTagName("a")[-2].text
        forum = int(re.sub(r"""<a href=['"]viewforum\.php\?id=(\d*)['"]>.*</a>""",r"\1",forum))
        header = document.getElementsByClass(f"pagelink conl")[0].getChildNodes()
        pages = [re.findall(r">(.+)<", x.text)[0] for x in header]
        pages = sorted(int(x) for x in pages if re.match(r"\d+", x))[-1]
        posts = [x.text for x in raw.getChildNodes()]
    return {"rawHTML": raw.text, "tID": topic, "fID": forum, "pages": pages, "posts": posts, "title": name}


__all__ = dir(globals())
