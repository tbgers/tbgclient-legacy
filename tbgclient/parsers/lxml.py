import datetime, re
import warnings
from lxml import etree


def get_post(document, pid=None):
    """Get post data using lxml."""
    # get the post
    document = etree.HTML(document)
    raw, tid, fid, user, text, time = (None,)*6 # le init

    err = document.find(".//div[@id='msg']")
    if err is not None:
        raw = etree.tostring(err)
    else:
        if pid is not None:
            # Check the "header"
            header = document.find(".//ul[@class='crumbs']").findall(".//a[@href]")
            tid = int(re.search(r"(\d+)", list(header[-1].values())[0]).group(1))
            fid = int(re.search(r"(\d+)", list(header[-2].values())[0]).group(1))

            # Check the post
            post = document.find(f".//div[@id='p{pid}']")
        else:
            post = document
            pid = int(document[0][0].get("id")[1:])

        if post is not None:
            user = etree.tostring(post.find(".//dl").find(".//dt")[0]).decode()[8:-9]
            text = etree.tostring(post.find(".//div[@class='postmsg']")).decode()
            text = re.search(r">(.*)</d",text,re.DOTALL).group(1).strip()
            time = post.find(".//a[@href]").text.split(" ")
            time[1] = datetime.datetime.strptime(time[1], "\u2009%H:%M:%S").time()
            if time[0] == "Today":
                time = datetime.datetime.combine(datetime.datetime.now().date(), time[1])
            elif time[0] == "Yesterday": 
                time = datetime.datetime.combine(datetime.datetime.now().date(), time[1])
                time += datetime.timedelta(days=-1)
            else:
                time = datetime.datetime.combine(datetime.datetime.strptime(time[0], "%Y-%b-%d").date(), time[1])
            time = str(time)
            raw = etree.tostring(post).decode()
        else:
            warnings.warn("Cannot find post ID in document", RuntimeWarning)
    return {"rawHTML": raw, "pID": pid, "tID": tid, "fID": fid, "user": user, "text": text, "time": time}


def get_element_by_id(document, id):
    document = etree.HTML(document).find(".//*[@id=%s]" % repr(id))
    if document is not None:
        return etree.tostring(document).decode()


def get_elements_by_class(document, klas):
    document = etree.HTML(document).findall(".//*[@class=%s]" % repr(klas))
    if document is not None:
        return [etree.tostring(x).decode() for x in document]


def get_elements_by_tag_name(document, tag):
    print(document, tag)
    document = etree.HTML(document).findall(".//%s" % tag)
    if document is not None:
        return [etree.tostring(x).decode() for x in document]


def get_user(document):
    a = etree.HTML(document)
    if a.findall('.//div[@class="blockmenu"]'): raise NotImplementedError
    a = a.findall(".//fieldset")
    a = [x.find(".//dl") for x in a]
    k = [x[::2] for x in a]
    v = [x[1::2] for x in a]
    a = [{p.text: q for p, q in zip(x, y)} for x, y in zip(k, v)]
    a = {k: v for x in a for k, v in x.items()}

    r = {}
    s = {}
    if "Username" in a:
        r["username"] = a["Username"].text
    if "Title" in a:
        r["title"] = a["Title"].text
    if "Location" in a:
        r["location"] = a["Location"].text
    if "Website" in a:
        r["website"] = a["Website"][0][0].get("href")
    if "Signature" in a:
        r["signature"] = "".join(etree.tostring(x).decode() for x in a["Signature"][0])
    if "Real name" in a:
        r["realname"] = a["Real name"].text
    if "Posts" in a:
        r["postcount"] = int(a["Posts"].text[:-3].replace(",", ""))
    if "Registered" in a:
        r["registered"] = datetime.datetime.strptime(a["Registered"].text, "%Y-%b-%d").date()

    if "Jabber" in a:
        s = a["Jabber"].text
    if "ICQ" in a:
        s = a["ICQ"].text
    if "MSN Messenger" in a:
        s = a["MSN Messenger"].text
    if "AOL IM" in a:
        s = a["AOL IM"].text
    if "Yahoo! Messenger" in a:
        s = a["Yahoo! Messenger"].text
    r["social"] = s
    return r


def get_page(document):
    """Get page data using lxml."""
    # get the post
    document = etree.HTML(document)
    raw, tid, fid, pages, posts = (None,)*5  # le init

    raw = document.find(".//div[@id='brdmain']")
    err = document.find(".//div[@id='msg']")
    if err is None:
        # Check the "header"
        header = document.find(".//ul[@class='crumbs']").findall(".//a[@href]")
        tid = int(re.search(r"(\d+)", list(header[-1].values())[0]).group(1))
        name = header[-1][0].text
        fid = int(re.search(r"(\d+)", list(header[-2].values())[0]).group(1))

        # Check the page count
        header = document.find(".//p[@class='pagelink conl']")
        pages = sorted(int(x.text) for x in header if re.match(r"\d+", x.text))[-1]

        # Check the post
        posts = [etree.tostring(x) for x in raw if re.match(r"p\d+", x.get("id") if x.get("id") is not None else "")]
    return {"rawHTML": etree.tostring(raw), "tID": tid, "fID": fid, "pages": pages, "posts": posts, "title": name}


def get_message(xml):
    """Get page data using lxml."""
    # it's literally copy-pasted from html.py
    # well the comment ruined it but you know what I mean
    xml = etree.XML(xml.encode())

    info = xml.find("infos")
    userlist = xml.find("users")
    msglist = xml.find("messages")

    if info is not None:
        info = {x.get("type"): x.text for x in info}

    users = {}
    if userlist is not None:
        for x in userlist:
            channel = x.get("channelID")
            if channel not in users: users[channel] = []
            users[channel].append({"uID": x.get("userID"), "username": x.text})

    messages = {}
    if msglist is not None:
        messages = [{
                        "pID": x.get("id"), 
                        "user": {"uID": x.get("userID"), "username": x[0].text.strip()},
                        "text": x[1].text.strip(),
                        "rawHTML": etree.tostring(x).decode(),
                        "time": datetime.datetime.strptime(x.get("dateTime"), "%a, %d %b %Y %H:%M:%S %z")
                    }
                    for x in msglist]
    return {"messages": messages, "info": info, "users": users}


__all__ = dir(globals())
