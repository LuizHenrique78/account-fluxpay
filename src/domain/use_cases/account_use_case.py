from utilities.depency_injections.injection_manager import utilities_injections

from src.application.schemas.acchount_schema import AccountSchema
from src.domain.entity.account import Account, AccountStatus
from src.infra.repositories.account_repository import AccountRepository

@utilities_injections
class AccountUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def create_account(self, account_data: AccountSchema):
        account = Account(
            tenant_id=account_data.tenant_id,
            owner_id=account_data.owner_id,
            status=AccountStatus.ACTIVE
        )
        return self.account_repository.create_account(account)


    def get_account(self, account_id: str):
        return self.account_repository.get_account_by_id(account_id)