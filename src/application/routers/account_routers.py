from fastapi import FastAPI

from utilities.frameworks.deployment_decorator import deployable

from src.application.schemas.acchount_schema import AccountSchema, GetAccountSchema
from src.domain.use_cases.account_use_case import AccountUseCase

app = FastAPI()


account_use_case = AccountUseCase()

@deployable(["cloudfunction", "fastapi"], methods=["POST"], schema_cls=AccountSchema, source="json", route="/accounts")
def create_account(account_schema: AccountSchema):
    """
    Create a new account.
    """
    account_data = account_use_case.create_account(account_schema)
    return {
        "message": "Account created successfully",
        "account_id": account_data
    }, 201


@deployable(["cloudfunction", "fastapi"], methods=["GET"], schema_cls=GetAccountSchema, source="json", route="/accounts")
def get_account(account_id: str):
    """
    Get account details by ID.
    """
    account_data = account_use_case.get_account(account_id)
    if not account_data:
        return {"message": "Account not found"}, 404
    return {
        "message": "Account retrieved successfully",
        "account": account_data
    }, 200