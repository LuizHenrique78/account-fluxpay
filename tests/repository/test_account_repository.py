import uuid

from utilities.logger.log_utils import Logger
from utilities.logger.logail_handler import LogtailHandler

from src.config.custom_config import ENVIRONMENT
from src.domain.entity.account import Account, AccountStatus

from src.infra.repositories.account_repository import AccountRepository


Logger.setup(LogtailHandler(), ENVIRONMENT.log_level)

account_repository = AccountRepository()

def _create_account():
     account = Account(
        tenant_id=str(uuid.uuid4()),
        owner_id=str(uuid.uuid4()),
        status=AccountStatus.ACTIVE
     ).generate_ulid()
     id = account_repository.create(account)
     response: Account = account_repository.get_by_id(id)
     return response

def test_create_account():
    data = Account(
        tenant_id=str(uuid.uuid4()),
        owner_id=str(uuid.uuid4()),
        status=AccountStatus.ACTIVE
    ).generate_ulid()
    response: str = account_repository.create(data)

    assert response is not ""

def test_create_account_with_id():
    data = Account(
        id="01JXN4DSSZPX14M9CK8BVV8TS8",  # This should not be set as it is auto-generated
        tenant_id="tenant_123",
        owner_id="owner_123",
        status=AccountStatus.ACTIVE
    )
    try:
        account_repository.create(data)
    except AccountRepositoryValidationException as e:
        assert str(e) == "cannot create account with id 01JXN4DSSZPX14M9CK8BVV8TS8"

def test_get_account():
    account_id = "01JXN4DSSZPX14M9CK8BVV8TS8"  # Replace with a valid account ID
    response: Account = account_repository.get_by_id(account_id)

    assert response is not None
    assert response.id == account_id
    assert response.status == AccountStatus.ACTIVE
    assert response.owner_id == "owner_123"
    assert response.tenant_id == "tenant_123"


def test_not_found_account():
    account_id = "non_existent_account_id"
    try:
        account_repository.get_by_id(account_id)
    except AccountNotFoundRepositoryException as e:
        assert str(e) == f"Account with ID {account_id} does not exist."


def test_update_account():
    account = _create_account()
    print(account)
    account.tenant_id = "tenant_123"
    account.owner_id = "owner_123"
    account.status = AccountStatus.CLOSED

    account_updated: Account = account_repository.update(account.id, account)
    response_account: Account = account_repository.get_by_id(account_updated.id)

    assert response_account.tenant_id == account.tenant_id
    assert response_account.owner_id == account.owner_id
    assert response_account.status == account.status
    assert response_account.id == account.id
    assert response_account.created_at is not None
    assert response_account.updated_at is not None

