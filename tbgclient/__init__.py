"""A TBG API wrapper for Python."""

__version__ = "0.1.0-a"
import glob, importlib, sys

# Import all
notAllowed = ["__init__"]
for i in glob.glob("tbgclient/*.py"):
    if "__init__.py" in i: continue
    mdl = importlib.import_module(f"tbgclient.{i[10:-3]}")
    imp_all = False
    if "_import_all" in dir(mdl): imp_all = mdl._import_all
    if i[10:-3] in dir(mdl) and not imp_all: mdl = getattr(mdl, i[10:-3])
    globals()[i[10:-3]] = mdl