from utilities.errors.errors import NotFound, BadRequest

class AccountRepositoryException(Exception):
    """Base exception for account repository errors."""
    def __init__(self, message: str = "An error occurred in the account repository."):
        super().__init__(message)


class AccountRepositoryValidationException(BadRequest):
    """Exception raised for validation errors in the account repository."""
    def __init__(self, message: str = "Validation error in the account repository."):
        super().__init__(message)


class AccountNotFoundRepositoryException(NotFound):
    """Exception raised when an account is not found in the repository."""
    def __init__(self, message: str = "Account not found in the repository."):
        super().__init__(message)


class AccountStatusRepositoryException(BadRequest):
    """Exception raised when there is an issue with the account status in the repository."""
    def __init__(self, message: str = "Account status error in the repository."):
        super().__init__(message)