from utilities.cross_cutting.application.schemas.responses_schema import SuccessResponse, ErrorResponse
from utilities.depency_injections.injection_manager import utilities_injections

from src.application.schemas.acchount_schema import AccountSchema, UpdateStatusAccountSchema
from src.domain.entity.account import Account, AccountStatus
from src.domain.services.account_service import AccountService


@utilities_injections
class AccountUseCase:
    """
    Application Use Case layer for Account operations.

    Responsibilities:
    - Handle API-level business logic.
    - Map request schemas to domain entities.
    - Call domain services.
    - Format and wrap responses.

    Features:
    - Account creation.
    - Account retrieval.
    - Account status updates with validation.
    """

    def __init__(self, account_service: AccountService):
        """
        Initializes the AccountUseCase with the required service dependency.

        Args:
            account_service (AccountService): Domain service handling business logic for accounts.
        """
        self.account_service = account_service


    def create_account(self, account_data: AccountSchema) -> SuccessResponse | ErrorResponse:
        """
        Creates a new account with default status ACTIVE.

        Business Rules:
        - New accounts always start as ACTIVE.
        - The caller provides only tenant_id and owner_id.

        Args:
            account_data (AccountSchema): Input data for account creation.

        Returns:
            SuccessResponse: If account creation succeeds.
            ErrorResponse: If creation fails due to validation or persistence issues.
        """
        account_data = Account(
            tenant_id=account_data.tenant_id,
            owner_id=account_data.owner_id,
            status=AccountStatus.ACTIVE
        )
        account: Account | ErrorResponse = self.account_service.create_account(account_data)

        if isinstance(account, Account):
            return SuccessResponse(status_code=200, body=account, message="Account created successfully")

        return account

    def get_account(self, account_id: str) -> SuccessResponse | ErrorResponse:
        """
        Retrieves an account by its ID.

        Args:
            account_id (str): The unique identifier of the account.

        Returns:
            SuccessResponse: If the account exists.
            ErrorResponse: If the account is not found.
        """
        account: Account | ErrorResponse = self.account_service.get_account(account_id)

        if isinstance(account, Account):
            return SuccessResponse(status_code=200, body=account, message="Account retrieved successfully")

        return account

    def update_status(self, update_status_schema: UpdateStatusAccountSchema) -> SuccessResponse | ErrorResponse:
        """
        Updates the status of an account, enforcing all business rules.

        Allowed Status Transitions:
            From ACTIVE:
                - ✅ To SUSPENDED (reason optional)
                - ✅ To CLOSED (reason optional)
            From SUSPENDED:
                - ✅ To ACTIVE (reason optional)
                - ✅ To CLOSED (reason recommended)
            From CLOSED:
                - ❌ No further transitions allowed.

        Validation Rules:
        - Cannot update to the same status.
        - Closing a SUSPENDED account should ideally have a reason.
        - Business rules enforced at the service layer.

        Args:
            update_status_schema (UpdateStatusAccountSchema): Contains `account_id`, target `status`, and optional `reason`.

        Returns:
            SuccessResponse: If status update succeeds.
            ErrorResponse: If validation fails or update fails.
        """
        account: Account | ErrorResponse = self.account_service.update_status(
            account_id=update_status_schema.account_id,
            update_status=AccountStatus(update_status_schema.status),
            reason=update_status_schema.reason
        )

        if isinstance(account, Account):
            return SuccessResponse(status_code=200, body=account, message="Account status updated successfully")

        return account
