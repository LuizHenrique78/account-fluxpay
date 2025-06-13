from utilities.depency_injections.injection_manager import InjectionManager
from utilities.depency_injections.utilities_injections import UtilitiesInjections

from src.domain.use_cases.account_use_case import AccountUseCase
from src.infra.repositories.account_repository import AccountRepository


def start_dependencies():
    """
    Starts the dependencies for the application.
    This function is called at the beginning of the application to ensure all necessary dependencies are running.
    """
    UtilitiesInjections.configure()
    InjectionManager.add_dependency(AccountRepository, AccountRepository("account"))
    InjectionManager.add_dependency(AccountUseCase, AccountUseCase())

