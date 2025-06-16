from utilities.errors.errors import BadRequest


class AccountUseCaseInvalidStatusException(BadRequest):
    """Exception raised when there is an issue with the account status in the repository."""
    def __init__(self, message: str = "Account status error in the domain/use_cases."):
        super().__init__(message)


class AccountServiceValidationException(BadRequest):
    """Exception raised for validation errors in the account service."""
    def __init__(self, message: str = "Validation error in the account service."):
        super().__init__(message)