from enum import Enum

from utilities.frameworks.base_entity.base_entity import BaseEntity


class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class Account(BaseEntity):
    tenant_id: str
    owner_id: str
    status: AccountStatus
    suspension_reason: str | None = None

    def __init__(self,**data):
        super().__init__(**data)
