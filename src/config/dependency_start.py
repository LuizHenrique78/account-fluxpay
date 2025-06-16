from utilities.depency_injections.injection_manager import InjectionManager
from utilities.depency_injections.utilities_injections import UtilitiesInjections

from src.application.use_cases.account_use_case import AccountUseCase

from src.domain.services.account_service import AccountService
from src.infra.repositories.account_repository import AccountRepository

def start_account_dependencies():
    """
    Initializes and registers all Account-related dependencies in the application's dependency injection container.

    This function should be called during the application startup phase.

    Responsibilities:
    - Configure global utility injections (e.g., logging, env vars, etc.).
    - Register repository, service, and use case dependencies for the Account domain.

    Registered Dependencies:
        - AccountRepository: Provides access to Firestore for Account entities.
        - AccountService: Contains business logic for account management.
        - AccountUseCase: Coordinates application-level logic for account operations.

    Usage:
        Call this function once at application startup (e.g., in your main.py or app entrypoint).

    Example:
        start_account_dependencies()
    """
    UtilitiesInjections.configure()

    # Account-related dependencies
    InjectionManager.add_dependency(AccountRepository, AccountRepository())
    InjectionManager.add_dependency(AccountService, AccountService())
    InjectionManager.add_dependency(AccountUseCase, AccountUseCase())
