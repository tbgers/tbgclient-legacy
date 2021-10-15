__version__ = "0.1.0-a"
import glob, importlib, sys
from tbgclient import parsers
from tbgclient.TBGSession import TBGSession

notAllowed = ["__init__","TBGSession"]
for i in glob.glob("tbgclient/*.py"):
    if "__init__.py" in i: continue
    globals()[i[10:-3]]=importlib.import_module("tbgclient." + i[10:-3])

