class InstagramException(Exception):
    pass


class AuthenticationError(InstagramException):
    pass


class TwoFactorAuthRequiredError(InstagramException):
    pass


class NoTwoFactorAuthPendingError(InstagramException):
    pass


class UserNotFoundError(InstagramException):
    pass


class AccessToDataDeniedError(InstagramException):
    pass
