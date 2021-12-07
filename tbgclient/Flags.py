from enum import Flag


class Flags(Flag):
    """Flags for tbgclient objects.
    These flags are used to control the behavior of an object.
    
    Flags
    -----
    NONE    : None.
    NO_LOGIN: Prevents logins on initialization.
    NO_INIT : Prevents other requests on initialization.
    RAW_DATA: Output raw data instead of tbgclient objects.
    """
    NONE = 0
    NO_LOGIN = 1 
    NO_INIT = 2
    RAW_DATA = 4
