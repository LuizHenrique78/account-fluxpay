import logging
from datetime import datetime
from pydantic import create_model

from utilities.cross_cutting.application.schemas.responses_schema import ErrorResponse, SuccessResponse, Process
from utilities.depency_injections.injection_manager import utilities_injections

from src.domain.entity.account import Account, AccountStatus
from src.domain.exceptions.account_service_exceptions import AccountServiceValidationException, \
    AccountServiceStatusException
from src.infra.repositories.account_repository import AccountRepository

logger = logging.getLogger(__name__)

@utilities_injections
class AccountService:
    """
    AccountService handles the business logic related to account management.

    Responsibilities:
    - Create new accounts.
    - Retrieve existing accounts.
    - Update account status with strict business validation.

    Business Rules for Status Management:
    - Possible statuses: ACTIVE, SUSPENDED, CLOSED.
    - From ACTIVE:
        - Can transition to SUSPENDED or CLOSED.
    - From SUSPENDED:
        - Can transition to ACTIVE or CLOSED.
    - From CLOSED:
        - No status changes allowed.
    """

    def __init__(self, account_repository: AccountRepository) -> None:
        """
        Initializes the AccountService with the required repository.

        :param account_repository: Repository for persisting and retrieving account entities.
        """
        self.account_repository = account_repository
        self._process = Process("service")

    def create_account(self, account_data: Account) -> Account | ErrorResponse:
        """
        Creates a new account.

        Business Rules:
        - The account ID must not be provided by the caller. It will be generated automatically.
        - If an ID is present in the input, the operation will fail with a validation exception.

        :param account_data: The Account object containing account details (without ID).
        :return: The ID of the newly created account.
        :raises AccountServiceValidationException: If an ID is provided in the input.
        """
        if account_data.id is not None:
            logger.warning(f"ID should not be provided when creating a new account")
            return ErrorResponse(message=f"cannot create account with id {account_data.id}", status_code=500, process=self._process)

        account_with_id = account_data.generate_ulid()
        id = self.account_repository.create(account_with_id)
        if not id:
            logger.error(f"Failed to create account with data: {account_data}")
            return ErrorResponse(message="Failed to create account", status_code=500, process=self._process)

        return account_with_id

    def get_account(self, account_id: str)-> Account | ErrorResponse:
        """
        Retrieves an account by its ID.

        :param account_id: The unique ID of the account to retrieve.
        :return: The Account object.
        :raises AccountNotFoundRepositoryException: If the account does not exist (from repository layer).
        """
        account: Account = self.account_repository.get_by_id(account_id)

        if not account:
            logger.error(f"Account with ID {account_id} not found")
            return ErrorResponse(message="Account not found", status_code=404)

        return account

    def update_status(self, account_id: str, update_status: AccountStatus, reason: str | None = None) -> Account | ErrorResponse:
        """
        Updates the status of an account, following strict business rules.

        Business Rules:
        - Cannot update to the same current status.
        - Status Transitions:
            - ACTIVE → SUSPENDED: Allowed. Reason is optional.
            - ACTIVE → CLOSED: Allowed. Reason is optional.
            - SUSPENDED → ACTIVE: Allowed. Reason is optional (current suspension reason is retained).
            - SUSPENDED → CLOSED: Allowed. Reason is optional.
            - CLOSED → Any: Not allowed. Closed accounts cannot change status.
        - Additional Rule:
            - When setting an account to CLOSED, a reason SHOULD be provided, though this is not currently enforced at code level.

        Audit Rule:
        - Updates the `updated_at` timestamp with the current date and time.

        :param account_id: The ID of the account to update.
        :param update_status: The new status to set (must be a valid AccountStatus enum).
        :param reason: Optional reason for the status change (especially relevant for SUSPENDED or CLOSED statuses).
        :return: The updated Account object.
        :raises AccountServiceStatusException: If the status transition is invalid according to the business rules.
        """

        if update_status == AccountStatus.SUSPENDED and not update_status:
            return ErrorResponse(message="Reason must be provided when closing an account", status_code=400, process=self._process)

        account: Account = self.account_repository.get_by_id(account_id)

        if update_status == account.status:
            return ErrorResponse(message=f"Account is already in {account.status} status", status_code=400, process=self._process)

        match account.status:
            case AccountStatus.ACTIVE:
                if update_status == AccountStatus.SUSPENDED:
                    account.status = AccountStatus.SUSPENDED
                    account.suspension_reason = reason
                elif update_status == AccountStatus.CLOSED:
                    account.status = AccountStatus.CLOSED
                    account.suspension_reason = reason

            case AccountStatus.SUSPENDED:
                if update_status == AccountStatus.ACTIVE:
                    account.status = AccountStatus.ACTIVE
                    account.suspension_reason = reason  # TODO: Review if the reason should be cleared when reactivating
                if update_status == AccountStatus.CLOSED:
                    account.status = AccountStatus.CLOSED
                    account.suspension_reason = reason

            case AccountStatus.CLOSED:
                return ErrorResponse(message="Cannot change status of a closed account", status_code=400, process=self._process)

        account.updated_at = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        updated_account: Account = self.account_repository.update(entity_id=account.id, entity=account)

        return updated_account