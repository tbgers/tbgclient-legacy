"""A modified copy of tbg-scraper's parsers."""
__all__ = "html lxml".split()
try:
    from tbgclient.parsers import html
    default = html
except: raise
try:
    from tbgclient.parsers import lxml
    default = lxml
except: pass