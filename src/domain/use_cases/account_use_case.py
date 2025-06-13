from src.application.schemas.acchount_schema import AccountSchema
from src.domain.entity.account import Account, AccountStatus
from src.infra.repositories.account_repository import AccountRepository


class AccountUseCase:
    def __init__(self):
        self.account_repository = AccountRepository("account")

    def create_account(self, account_data: AccountSchema):
        account = Account(
            tenant_id=account_data.tenant_id,
            owner_id=account_data.owner_id,
            status=AccountStatus.ACTIVE
        )
        return self.account_repository.create_account(account)


    def get_account(self, account_id: str):
        return self.account_repository.get_account_by_id(account_id)