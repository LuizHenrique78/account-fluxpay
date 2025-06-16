from utilities.depency_injections.injection_manager import InjectionManager
from utilities.depency_injections.utilities_injections import UtilitiesInjections

from src.application.use_cases.account_use_case import AccountUseCase
from src.domain.entity.account import Account
from src.domain.services.account_service import AccountService
from src.infra.repositories.account_repository import AccountRepository


def start_account_dependencies():
    """
    Starts the dependencies for the Account application.
    This function is called at the beginning of the application to ensure all necessary dependencies are running.
    """
    UtilitiesInjections.configure()

    #account_dependencies
    InjectionManager.add_dependency(AccountRepository, AccountRepository("account", Account))
    InjectionManager.add_dependency(AccountService, AccountService())
    InjectionManager.add_dependency(AccountUseCase, AccountUseCase())

