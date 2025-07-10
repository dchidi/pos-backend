class UserNotFound(Exception):
    pass

class InvalidUserId(Exception):
    pass

class EmailAlreadyExists(Exception):
    pass

class InvalidCredentials(Exception):
    pass

class OTPExpired(Exception):
    pass

class OTPNotFound(Exception):
    pass

class OTPAttemptsExceeded(Exception):
    pass

class InvalidOTP(Exception):
    pass

class RoleNotFound(Exception):
    pass

class InvalidPermissionSet(Exception):
    pass

class RoleExists(Exception):
    pass