from utilities.cross_cutting.application.schemas.responses_schema import SuccessResponse, ErrorResponse
from utilities.depency_injections.injection_manager import InjectionManager

from src.domain.entity.account import Account, AccountStatus
from src.domain.services.account_service import AccountService

service = InjectionManager.get_dependency(AccountService)

def _create_account_service():
    account = Account(
        tenant_id="Test Account",
        owner_id="email@email.com",
        status=AccountStatus.ACTIVE,
    )

    created_account: Account = service.create_account(account)
    account: Account = service.get_account(created_account.id)
    return account


def test_create_account():
    account = Account(
        tenant_id="Test Account",
        owner_id="email@email.com",
        status=AccountStatus.ACTIVE,
    )

    created_account: Account = service.create_account(account)

    assert created_account.id == account.id


def test_get_account():
    account = _create_account_service()
    account_data: Account = service.get_account(account.id)

    assert account_data is not None
    assert account_data.id is not None
    assert account_data.created_at is not None
    assert account_data.tenant_id == "Test Account"
    assert account_data.owner_id == "email@email.com"

def test_update_status_active_to_suspend():
    account = _create_account_service()

    response_updated: Account = service.update_status(account.id, AccountStatus.SUSPENDED, "Testing suspension")

    assert response_updated is not None
    assert isinstance(response_updated, Account)
    assert response_updated.id == account.id
    assert response_updated.status == AccountStatus.SUSPENDED
    assert response_updated.suspension_reason == "Testing suspension"
    assert response_updated.tenant_id == account.tenant_id
    assert response_updated.owner_id == account.owner_id
    assert response_updated.created_at is not None
    assert response_updated.updated_at is not None

def test_update_status_closed_to_active_error():
    account = _create_account_service()
    updated_account: Account = service.update_status(account.id, AccountStatus.CLOSED)

    assert updated_account.status == AccountStatus.CLOSED

    response: ErrorResponse  = service.update_status(account.id, AccountStatus.ACTIVE)

    if isinstance(response, ErrorResponse):
        assert response.message == "Cannot change status of a closed account"
        assert response.status_code == 400



def test_update_status_active_to_active_error():
    account = _create_account_service()

    response: ErrorResponse = service.update_status(account.id, AccountStatus.ACTIVE)
    if isinstance(response, ErrorResponse):
        assert response.message == f"Account is already in {account.status} status"
        assert response.status_code == 400
