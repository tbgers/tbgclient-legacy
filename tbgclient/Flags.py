from enum import IntFlag


class Flags(IntFlag):
    """Flags for tbgclient objects.

    These flags are used to control the behavior of an object.

    Flags
    -----
    NONE        : None.
    NO_LOGIN    : Prevents logins on initialization.
    NO_INIT     : Prevents other requests on initialization.
    RAW_DATA    : Output raw data instead of tbgclient objects.
                  Could improve performance.
    MULTI_USER  : Use api.SessionM instead of requests.Session.
                  Useful if you have multiple TBGSessions.
    """
    NONE = 0
    NO_LOGIN = 1
    NO_INIT = 2
    RAW_DATA = 4
    MULTI_USER = 8
