from enum import Enum
from utilities.cross_cutting.domain.entities.base_entity import BaseEntity

class AccountStatus(str, Enum):
    """
    Enumeration for possible account statuses.

    Status Values:
        - ACTIVE: The account is currently active and usable.
        - SUSPENDED: The account is temporarily suspended.
        - CLOSED: The account is permanently closed and cannot be reactivated.

    Usage Example:
        status = AccountStatus.ACTIVE
    """
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class Account(BaseEntity):
    """
    Domain entity representing an Account.

    Attributes:
        tenant_id (str): The tenant to which this account belongs (multi-tenancy support).
        owner_id (str): The ID of the user who owns this account.
        status (AccountStatus): The current status of the account.
        suspension_reason (Optional[str]): Reason for suspension or closure, if applicable.

    Inherits:
        BaseEntity: Provides base fields like 'id', 'created_at', and 'updated_at'.

    Business Notes:
        - Accounts can only transition between statuses according to the defined business rules.
        - The 'suspension_reason' field is typically used when the account is suspended or closed.

    Example:
        account = Account(
            tenant_id="tenant_123",
            owner_id="user_456",
            status=AccountStatus.ACTIVE
        )
    """

    tenant_id: str
    owner_id: str
    status: AccountStatus
    suspension_reason: str | None = None

    def __init__(self, **data):
        """
        Initializes an Account entity.

        Args:
            **data: Arbitrary keyword arguments matching the Account fields.
        """
        super().__init__(**data)
