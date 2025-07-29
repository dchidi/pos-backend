class ServiceError(Exception):
    """Base exception for service layer errors"""
    pass

class NotFoundError(ServiceError):
    """Raised when an entity is not found in database"""
    pass

class AlreadyExistsError(ServiceError):
    """Raised when attempting to create a duplicate entity"""
    pass

class ValidationError(ServiceError):
    """Raised when input data fails business validation"""
    pass

class OTPAttemptsExceeded(Exception):    
    """Raised when user exceeds number of attempts on otp sent to email address"""
    pass

class OTPExpired(Exception):
    pass

class InvalidOTP(Exception):
    pass

class OTPNotFound(Exception):
    pass

class UnAuthorized(Exception):
    pass

class ResetPassword(Exception):
    pass

# Delete below later
class UserNotFound(Exception):
    pass 
class InvalidUserId(Exception):
    pass 
class EmailAlreadyExists(Exception):
    pass
class InvalidPermissionSet(ServiceError):
    pass
class InvalidCredentials(ServiceError):
    pass