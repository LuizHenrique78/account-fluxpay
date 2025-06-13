import datetime

from google.cloud import firestore
from utilities.frameworks.base_entity.base_entity import BaseEntity

from src.domain.entity.account import Account, AccountStatus
from src.infra.exceptions.repositories.account_repository_exceptions import AccountNotFoundRepositoryException, \
    AccountStatusRepositoryException


class AccountRepository:
    def __init__(self, collection_name: str):
        # Initialize the Firestore client
        self.client = firestore.Client()
        self.collection = self.client.collection(collection_name)

    def get_account_by_id(self, account_id: str) -> Account | None:
        doc = self.collection.document(account_id).get()

        if doc.exists:
            return Account(id=doc.id, **doc.to_dict())

        raise AccountNotFoundRepositoryException(f"Account with ID {account_id} does not exist.")

    def create_account(self, account_data: Account):
        """ Creates a new account in Firestore.
        If the account already exists, it raises an exception.
        """
        model = account_data.generate_ulid()
        self._save(model)
        return model.id

    def update_account(self, account_id: str, account_data: Account):
        """
        Updates an existing account in Firestore.
        If the account does not exist, it raises an exception.
        """
        doc_ref = self.collection.document(account_id)
        if not doc_ref.get().exists:
            raise AccountNotFoundRepositoryException(f"Account with ID {account_id} does not exist.")

        self._save(account_data)

    def disable_account(self, account_id: str):
        ...

    def update_status(self, account_id: str, status: AccountStatus):
        doc = self.collection.document(account_id).get()
        account = Account(id=doc.id, **doc.to_dict())

        if account.status == AccountStatus.CLOSED:
            raise AccountStatusRepositoryException("account closed cannot be modified")

        account.status = status
        self._save(account)


    def _save(self, model: BaseEntity) -> bool:
        """
        Saves the Pydantic model to Firestore. Returns the document ID.
        If the model has an 'id' attribute, uses it as the document ID.
        Otherwise, generates a ULID as the ID.
        """
        data = model.model_dump(exclude_none=True, exclude={"_id"})

        doc_ref = self.collection.document(model.id)
        write_result = doc_ref.set(data)
        if write_result is None:
            return False
        return True