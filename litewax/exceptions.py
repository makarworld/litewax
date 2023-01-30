class AuthNotFound(Exception):
    """Raised when no auth is found"""
    pass

class SessionExpired(Exception):
    """Raised when session is expired or token is invalid"""
    pass

class SignError(Exception):
    """Raised when signing fails"""
    pass

class UnknownError(Exception):
    """Raised when unknown error occurs"""
    pass

class CPUlimit(Exception):
    """Raised when CPU limit is reached"""
    pass

class ExpiredTransaction(Exception):
    """Raised when transaction is expired"""
    pass

class NotImplementedError(Exception):
    """Raised when method is not implemented"""
    pass

class CookiesExpired(Exception):
    """Raised when cookies are expired or invalid"""
    pass

class AtomicHubPushError(Exception):
    """Raised when transaction is not signed by AtomicHub"""
    pass

class NeftyBlocksPushError(Exception):
    """Raised when transaction is not signed by NeftyBlocks"""
    pass