import requests, datetime, re
import warnings
from lxml import etree

def get_post(document,id):
    """Get post data by PID using lxml"""
    # get the post
    document = etree.HTML(document)
    raw, tid, fid, user, text, time = (None,)*6 # le init

    err = document.find(".//div[@id='msg']")
    if err is not None:
        raw = etree.tostring(err)
    else:
        # Check the "header"
        header = document.find(".//ul[@class='crumbs']").findall(".//a[@href]")
        tid = int(re.search("(\d+)",list(header[-1].values())[0]).group(1))
        fid = int(re.search("(\d+)",list(header[-2].values())[0]).group(1))

        # Check the post
        post = document.find(f".//div[@id='p{id}']")
        if post is not None:
            user = post.find(".//dl").find(".//dt")[0].text
            text = etree.tostring(post.find(".//div[@class='postmsg']")[0]).decode()
            time = post.find(".//a[@href]").text.split(" ")
            time[1] = datetime.datetime.strptime(time[1],"\u2009%H:%M:%S").time()
            if time[0] == "Today": time = datetime.datetime.combine(datetime.datetime.now().date(),time[1])
            elif time[0] == "Yesterday": 
                time = datetime.datetime.combine(datetime.datetime.now().date(),time[1])
                time += datetime.timedelta(days=-1)
            else: time = datetime.datetime.combine(datetime.datetime.strptime(time[0],"%Y-%b-%d").date(),time[1])
            time = str(time)
            raw = etree.tostring(post).decode()
        else: warnings.warn("Cannot find post ID in document",RuntimeWarning)
    return {"rawHTML":raw,"pid":id,"tid":tid,"fid":fid,"user":user,"text":text,"time":time}

def get_element_by_id(document, id):
    document = etree.HTML(document).find(".//*[@id=%s]" % repr(id))
    if document is not None: return etree.tostring(document).decode()

def get_elements_by_class(document, klas):
    document = etree.HTML(document).findall(".//*[@class=%s]" % repr(klas))
    if document is not None: return [etree.tostring(x).decode() for x in document]

def get_elements_by_tag_name(document, tag):
    print(document, tag)
    document = etree.HTML(document).findall(".//%s" % tag)
    if document is not None: return [etree.tostring(x).decode() for x in document]

__all__ = dir(globals())