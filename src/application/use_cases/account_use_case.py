from utilities.cross_cutting.application.schemas.responses_schema import SuccessResponse, ErrorResponse, Process
from utilities.depency_injections.injection_manager import utilities_injections

from src.application.schemas.acchount_schema import AccountSchema, UpdateStatusAccountSchema
from src.domain.entity.account import Account, AccountStatus
from src.domain.services.account_service import AccountService


@utilities_injections
class AccountUseCase:
    """
    Use case class responsible for account-related business logic,
    including creation, retrieval, and status updates.
    """

    def __init__(self, account_service: AccountService):
        """
        Initializes the AccountUseCase with a given account repository.

        :param account_service: A repository for managing Firestore Account persistence.
        """
        self.account_service = account_service
        self._process = Process("use_case")

    def create_account(self, account_data: AccountSchema) -> SuccessResponse | ErrorResponse:
        """
        Creates a new account with ACTIVE status.

        :param account_data: AccountSchema object containing tenant_id and owner_id.
        :return: The created Account object.
        """
        account = Account(tenant_id=account_data.tenant_id, owner_id=account_data.owner_id, status=AccountStatus.ACTIVE)
        response: SuccessResponse | ErrorResponse  = self.account_service.create_account(account)
        response.process = self._process
        if isinstance(response, SuccessResponse):
            response.data = response.data.model_dump(exclude_none=True)

        return response

    def get_account(self, account_id: str)-> SuccessResponse | ErrorResponse:
        """
        Retrieves an account by its ID.

        :param account_id: The unique identifier of the account.
        :return: Account object if found, otherwise None.
        """
        response: SuccessResponse | ErrorResponse = self.account_service.get_account(account_id)
        response.process = self._process
        if isinstance(response, SuccessResponse):
            response.data = response.data.model_dump(exclude_none=True)

        return response

    def update_status(self, update_status_schema: UpdateStatusAccountSchema) -> SuccessResponse | ErrorResponse:
        """
        Update the status of an account according to business rules.

        Allowed status transitions:
        - From ACTIVE:
            - ✅ Can move to SUSPENDED (reason optional)
            - ✅ Can move to CLOSED (reason optional)
        - From SUSPENDED:
            - ✅ Can move to ACTIVE (reactivation, reason optional)
            - ✅ Can move to CLOSED (reason required)
        - From CLOSED:
            - ❌ Cannot change status (any attempt will raise exception)

        Additional validation rules:
        - Updating to the same current status is not allowed (will raise exception).
        - Closing a SUSPENDED account requires a reason (will raise exception if missing).

        Args:
            update_status_schema (UpdateStatusAccountSchema): Contains `account_id`, target `status`, and optional `reason`.

        Raises:
            AccountUseCaseInvalidStatusException: If the status transition is not allowed,
                                                  if trying to close without reason,
                                                  or if status remains the same.

        Returns:
            Account | None: The updated Account object if successful, or None if update failed.
        """
        response: SuccessResponse | ErrorResponse = self.account_service.update_status(
            account_id=update_status_schema.account_id,
            update_status=AccountStatus(update_status_schema.status),
            reason=update_status_schema.reason
        )
        response.process = self._process
        if isinstance(response, SuccessResponse):
            response.data = response.data.model_dump(exclude_none=True)

        return response
