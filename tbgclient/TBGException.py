import warnings
_import_all = True # flag to import all
class TBGException(Exception):
    """The class for all tbgclient exceptions."""
    pass

class RequestException(TBGException):
    """This exception is for request-related errors."""
    pass

class CredentialsException(TBGException):
    """This exception is for account-related errors."""
    pass

class TBGWarning(Warning):
    """The class for all tbgclient warnings."""
    pass