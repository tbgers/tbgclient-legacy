from enum import Enum


class Flags(Enum):
    NO_LOGIN = 1  # This flag is to prevent logins on initialization.
    NO_INIT = 2  # This flag is to prevent other requests on initialization.
