from utilities.cross_cutting.infra.repositories.firestore_base_repository import FirestoreBaseRepository
from utilities.depency_injections.injection_manager import utilities_injections

@utilities_injections
class AccountRepository(FirestoreBaseRepository):
    ...