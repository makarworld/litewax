
from calendar import c


class AuthNotFound(Exception):
    pass

class SessionExpired(Exception):
    pass

class SignError(Exception):
    pass

class UnknownError(Exception):
    pass

class CPUlimit(Exception):
    pass

class ExpiredTransaction(Exception):
    pass

class NotImplementedError(Exception):
    pass

class CookiesExpired(Exception):
    pass

class PayWithPushError(Exception):
    pass