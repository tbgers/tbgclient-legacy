"""Parsers for tbgclient.

This is a modified copy of tbg-scraper's parsers."""
__all__ = "html lxml".split()
from tbgclient.parsers import html
default = html
try:
    from tbgclient.parsers import lxml
    default = lxml
except:
    print("Cannot use lxml, using html instead")
