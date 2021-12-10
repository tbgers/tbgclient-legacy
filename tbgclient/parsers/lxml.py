import datetime, re
import warnings
from lxml import etree


def get_post(document, id):
    """Get post data using lxml."""
    # get the post
    document = etree.HTML(document)
    raw, tid, fid, user, text, time = (None,)*6 # le init

    err = document.find(".//div[@id='msg']")
    if err is not None:
        raw = etree.tostring(err)
    else:
        # Check the "header"
        header = document.find(".//ul[@class='crumbs']").findall(".//a[@href]")
        tid = int(re.search(r"(\d+)", list(header[-1].values())[0]).group(1))
        fid = int(re.search(r"(\d+)", list(header[-2].values())[0]).group(1))

        # Check the post
        post = document.find(f".//div[@id='p{id}']")
        if post is not None:
            user = etree.tostring(post.find(".//dl").find(".//dt")[0]).decode()[8:-9]
            text = etree.tostring(post.find(".//div[@class='postmsg']")[0]).decode()
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
    return {"rawHTML": raw, "pid": id, "tid": tid, "fid": fid, "user": user, "text": text, "time": time}


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
    a = etree.HTML(document).findall(".//fieldset")
    if a.findall(".//div[@class=blockmenu]"): raise NotImplementedError
    a = [x.find(".//dl") for x in a]
    k = [x[::2] for x in a]
    v = [x[1::2] for x in a]
    a = [{p.text: q for p, q in zip(x, y)} for x, y in zip(k, v)]
    a = {k: v for x in a for k, v in x.items()}
    
    r = {
        "username": a["Username"].text,
        "title": a["Title"].text,
        "location": a["Location"].text,
        "website": a["Website"][0][0].get("href"),
        "signature": "".join(etree.tostring(x).decode() for x in a["Signature"][0]),
        "realname": a["Real name"].text,
        "social": {
            "Jabber": a["Jabber"].text,
            "ICQ": a["ICQ"].text,
            "MSN Messenger": a["MSN Messenger"].text,
            "AOL IM": a["AOL IM"].text,
            "Yahoo! Messenger": a["Yahoo! Messenger"].text
        },
        "postcount": int(a["Posts"].text[:-3].replace(",", "")),
        "registered": datetime.datetime.strptime(a["Registered"].text, "%Y-%b-%d").date()
    }
    return r

__all__ = dir(globals())
