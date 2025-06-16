from utilities.errors.errors import BadRequest


class AccountServiceValidationException(BadRequest):
    """Exception raised for validation errors in the account service."""
    def __init__(self, message: str = "Validation error in the account service."):
        super().__init__(message)


class AccountServiceStatusException(BadRequest):
    """Exception raised when there is an issue with the account status in the service."""
    def __init__(self, message: str = "Account status error in the service."):
        super().__init__(message)