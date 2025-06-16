from utilities.cross_cutting.infra.repositories.firestore_base_repository import FirestoreBaseRepository
from utilities.depency_injections.injection_manager import utilities_injections
from src.domain.entity.account import Account

@utilities_injections
class AccountRepository(FirestoreBaseRepository[Account]):
    """
    Repository for managing Account entities in Firestore.

    Inherits all basic CRUD operations from FirestoreBaseRepository.

    Responsibilities:
    - Persist and retrieve Account entities.
    - Map Firestore documents to the Account domain model.
    - Provide a dedicated repository interface for the Account domain.

    Dependencies:
    - Firestore (Google Cloud Firestore)
    - Dependency Injection via utilities_injections

    Usage:
        account_repo = AccountRepository()
        account = account_repo.get_by_id(account_id)
        account_repo.create(account)
        account_repo.update(account.id, account)
        account_repo.delete(account.id)
    """

    def __init__(self):
        """
        Initializes the AccountRepository with the 'accounts' collection.

        Automatically injects dependencies via utilities_injections.
        """
        super().__init__(collection_name="accounts", model_class=Account)
