from pydantic import BaseModel


class AccountSchema(BaseModel):
    """
    Schema for account-related operations.

    This schema defines the structure of the data used in account operations,
    including fields for account ID, name, and email.
    """
    tenant_id: str
    owner_id: str

    class Config:
        validate_assignment = True


class GetAccountSchema(BaseModel):
    """
    Schema for retrieving account information.

    Inherits from AccountSchema and can be extended with additional fields
    specific to retrieval operations if needed.
    """
    account_id: str