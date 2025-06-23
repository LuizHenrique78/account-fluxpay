import logging
from datetime import datetime

from utilities.cross_cutting.application.schemas.responses_schema import ErrorResponse, ErrorMessage

from src.domain.entity.account import Account, AccountStatus

from src.infra.repositories.account_repository import AccountRepository

logger = logging.getLogger(__name__)


class AccountService:
    """
    Service layer responsible for managing accounts and enforcing business rules.

    Responsibilities:
    - Create new accounts.
    - Retrieve existing accounts.
    - Update account status while applying business validations.

    Status Transition Rules:
    - Possible statuses: ACTIVE, SUSPENDED, CLOSED.

    From ACTIVE:
        - Allowed transitions: SUSPENDED, CLOSED.

    From SUSPENDED:
        - Allowed transitions: ACTIVE, CLOSED.

    From CLOSED:
        - No further transitions allowed.

    Additional Notes:
    - When transitioning to CLOSED, a reason SHOULD be provided (currently not enforced at code level).
    - Updating status also updates the `updated_at` timestamp.
    """

    def __init__(self, account_repository: AccountRepository) -> None:
        """
        Initializes the AccountService with its dependencies.

        :param account_repository: The repository used for persisting and retrieving Account entities.
        """
        self.account_repository = account_repository

    def create_account(self, account_data: Account) -> Account | ErrorResponse:
        """
        Creates a new account.

        Business Rules:
        - The account ID must not be provided by the client. It is generated internally.
        - If an ID is present in the input, the creation will fail with a validation error.

        :param account_data: The Account object with initial account data (without ID).
        :return: The created Account object with generated ID, or ErrorResponse in case of failure.
        """
        if account_data.id is not None:
            logger.warning(f"Account creation failed: ID should not be provided. Received ID: {account_data.id}")
            return ErrorResponse(
                body=ErrorMessage(error="Internal Server Error"),
                message=f"Cannot create account with id {account_data.id}",
                status_code=400,
            )

        account_with_id = account_data.generate_ulid()
        id = self.account_repository.create(account_with_id)

        if not id:
            logger.error(f"Failed to persist account: {account_data}")
            return ErrorResponse(
                body=ErrorMessage(error="Failed to create account"),
                message="Internal Server Error",
                status_code=500,
            )

        return account_with_id

    def get_account(self, account_id: str) -> Account | ErrorResponse:
        """
        Retrieves an account by its unique ID.

        :param account_id: The unique identifier of the account.
        :return: The Account object if found, or ErrorResponse if not found.
        """
        account: Account = self.account_repository.get_by_id(account_id)
        # TODO: cahnge satatus code to 204
        if not account:
            logger.error(f"Account with ID {account_id} not found")
            return ErrorResponse(
                body=ErrorMessage(error="Account not found"),
                message="Account not found",
                status_code=404,
            )

        return account

    def update_status(self, account_id: str, update_status: AccountStatus, reason: str | None = None) -> Account | ErrorResponse:
        """
        Updates the status of an account while validating business rules.

        Business Rules:
        - Cannot update to the same current status.
        - Status Transitions:
            - ACTIVE → SUSPENDED: Allowed. Reason is optional.
            - ACTIVE → CLOSED: Allowed. Reason is optional (but recommended).
            - SUSPENDED → ACTIVE: Allowed.
            - SUSPENDED → CLOSED: Allowed. Reason is optional.
            - CLOSED → Any: Not allowed.

        Additional Notes:
        - When setting an account to CLOSED, providing a reason is recommended (though not enforced in code).
        - Updates the `updated_at` field with the current timestamp.

        :param account_id: The ID of the account to update.
        :param update_status: The new AccountStatus to set.
        :param reason: Optional reason for the status change.
        :return: The updated Account object, or ErrorResponse if validation fails.
        """
        account: Account = self.account_repository.get_by_id(account_id)

        if not account:
            logger.error(f"Account with ID {account_id} not found for status update")

            return ErrorResponse(
                body=ErrorMessage(error="Account not found"),
                message="Account not found",
                status_code=404,
            )

        if update_status == account.status:
            logger.warning(f"Account {account_id} is already in status {account.status}")
            return ErrorResponse(
                body=ErrorMessage(error=f"Account is already in {account.status} status"),
                message=f"Bad Request",
                status_code=409,
            )

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
                    account.suspension_reason = reason  # Optional: Could be cleared here if needed
                elif update_status == AccountStatus.CLOSED:
                    account.status = AccountStatus.CLOSED
                    account.suspension_reason = reason

            case AccountStatus.CLOSED:
                logger.error(f"Attempted status change on CLOSED account {account_id}")
                return ErrorResponse(
                    body=ErrorMessage(error="Cannot change status of a closed account"),
                    message="Bad Request",
                    status_code=400,
                )

        account.updated_at = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        updated_account: Account = self.account_repository.update(entity_id=account.id, entity=account)

        return updated_account
