from utilities.cross_cutting.application.schemas.responses_schema import SuccessResponse, ErrorResponse
from utilities.depency_injections.injection_manager import InjectionManager

from src.application.schemas.acchount_schema import AccountSchema, UpdateStatusAccountSchema
from src.domain.entity.account import Account, AccountStatus

from src.application.use_cases.account_use_case import AccountUseCase


account_use_case = InjectionManager.get_dependency(AccountUseCase)

def _create_account():
    model = AccountSchema(
        tenant_id="tenant123",
        owner_id="owner456"
    )
    account = account_use_case.create_account(model)
    return account.body


def test_create_account():
    model = AccountSchema(
        tenant_id="tenant123",
        owner_id="owner456"
    )
    response = account_use_case.create_account(model)

    assert response is not None
    assert isinstance(response, SuccessResponse)
    assert response.status_code == 200
    assert response.message == "Account created successfully"
    assert response.body is not None


def test_get_account():
    account = _create_account()  # Replace with a valid account ID for testing
    response: Account = account_use_case.get_account(account.id)

    assert response is not None
    assert response.status_code == 200
    assert response.body.id is not None
    assert response.body.tenant_id == account.tenant_id
    assert response.body.owner_id == account.owner_id
    assert response.body.created_at is not None


def test_update_status_active_to_suspend():
    account = _create_account()
    schema_update_status = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.SUSPENDED, reason="Testing suspension")

    response = account_use_case.update_status(schema_update_status)

    response_updated = account_use_case.get_account(account.id)

    assert response is not None
    assert response_updated.status_code == 200
    assert response_updated.body.id == account.id
    assert response_updated.body.status == AccountStatus.SUSPENDED
    assert response_updated.body.suspension_reason == "Testing suspension"
    assert response_updated.body.tenant_id == account.tenant_id
    assert response_updated.body.owner_id == account.owner_id
    assert response_updated.body.created_at is not None
    assert response_updated.body.updated_at is not None


def test_update_status_closed_to_active_error():
    account = _create_account()
    schema_update_status = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.CLOSED)
    account_use_case.update_status(schema_update_status)

    new_status_schema = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.ACTIVE)

    response: ErrorResponse = account_use_case.update_status(new_status_schema)
    assert response.status_code == 400
    assert response.message == "Bad Request"
    assert response.body.error == "Cannot change status of a closed account"


def test_update_status_active_to_active_error():
    account = _create_account()
    schema_update_status = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.ACTIVE)

    response: ErrorResponse = account_use_case.update_status(schema_update_status)

    assert response.status_code == 409
    assert response.message == "Bad Request"
    assert response.body.error == f"Account is already in {account.status} status"
