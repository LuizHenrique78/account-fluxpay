from utilities.depency_injections.injection_manager import InjectionManager

from src.application.schemas.acchount_schema import AccountSchema, UpdateStatusAccountSchema
from src.config.dependency_start import start_account_dependencies
from src.domain.entity.account import Account, AccountStatus

from src.application.use_cases.account_use_case import AccountUseCase
from src.domain.exceptions.account_service_exceptions import AccountServiceStatusException


account_use_case = InjectionManager.get_dependency(AccountUseCase)

def _create_account():
    model = AccountSchema(
        tenant_id="tenant123",
        owner_id="owner456"
    )
    id = account_use_case.create_account(model)
    account = account_use_case.get_account(id)
    return account


def test_create_account():
    model = AccountSchema(
        tenant_id="tenant123",
        owner_id="owner456"
    )
    response = account_use_case.create_account(model)

    assert response is not None
    assert isinstance(response, str)  # Assuming the response is an account ID


def test_get_account():
    account = _create_account()  # Replace with a valid account ID for testing
    response: Account = account_use_case.get_account(account.id)

    assert response is not None
    assert isinstance(response, Account)


def test_update_status_active_to_suspend():
    account = _create_account()
    schema_update_status = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.SUSPENDED, reason="Testing suspension")

    response = account_use_case.update_status(schema_update_status)
    response_updated = account_use_case.get_account(response.id)

    assert response is not None
    assert isinstance(response, Account)
    assert response_updated.id == response.id
    assert response_updated.status == AccountStatus.SUSPENDED
    assert response_updated.suspension_reason == "Testing suspension"
    assert response_updated.tenant_id == account.tenant_id
    assert response_updated.owner_id == account.owner_id
    assert response_updated.created_at is not None
    assert response_updated.updated_at is not None


def test_update_status_closed_to_active_error():
    account = _create_account()
    schema_update_status = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.CLOSED)
    account_use_case.update_status(schema_update_status)

    new_status_schema = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.ACTIVE)
    try:
        response = account_use_case.update_status(new_status_schema)
    except AccountServiceStatusException as e:
        assert str(e) == "Cannot change status of a closed account"


def test_update_status_active_to_active_error():
    account = _create_account()
    schema_update_status = UpdateStatusAccountSchema(account_id=account.id, status=AccountStatus.ACTIVE)
    try:
        account_use_case.update_status(schema_update_status)
    except AccountServiceStatusException as e:
        assert str(e) == f"Account is already in {account.status} status"