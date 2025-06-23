from utilities.cross_cutting.application.routers.http_response_adapter import to_lambda_http_response
from utilities.cross_cutting.application.schemas.responses_schema import SuccessResponse, ErrorResponse
from utilities.depency_injections.injection_manager import InjectionManager
from utilities.frameworks.deployment_decorator import deployable
from utilities.frameworks.deployment_target import DeploymentTarget

from src.application.schemas.acchount_schema import AccountSchema, GetAccountSchema, UpdateStatusAccountSchema
from src.config.dependency_start import start_account_dependencies
from src.application.use_cases.account_use_case import AccountUseCase
from src.domain.services.account_service import AccountService
from src.infra.repositories.account_repository import AccountRepository

start_account_dependencies()

account_use_case = AccountUseCase(
    account_service=AccountService(account_repository=InjectionManager.get_dependency(AccountRepository))
)

LAMBDA_TARGET = DeploymentTarget.LAMBDA
FASTAPI_TARGET = DeploymentTarget.FASTAPI

@deployable(
    [LAMBDA_TARGET, FASTAPI_TARGET],
    methods=["POST"],
    schema_cls=AccountSchema,
    source="json",
    route="/accounts/create"
)
def create_account(account_schema: AccountSchema):
    """
    Endpoint to create a new account.

    Supported Deployment Types:
        - Google Cloud Function
        - FastAPI

    HTTP Method:
        POST

    Route:
        fastapi: /accounts/create
        cloud-function: /create_account

    Request Body:
        AccountSchema: Contains tenant_id and owner_id.

    Response:
        SuccessResponse: Account created successfully.
        ErrorResponse: In case of validation or persistence failure.
    """
    response: SuccessResponse | ErrorResponse = account_use_case.create_account(account_schema, create_account)
    return to_lambda_http_response(response)


@deployable(
    [LAMBDA_TARGET],
    methods=["GET"],
    schema_cls=GetAccountSchema,
    source="path",
    route="/accounts/{accountId}"
)
def get_account(get_schema: GetAccountSchema):
    """
    Endpoint to retrieve an account by ID.

    Supported Deployment Types:
        - Google Cloud Function
        - FastAPI

    HTTP Method:
        GET

    Route:
        fastapi: /accounts/get
        cloud-function: /get_account

    Query Parameters:
        GetAccountSchema: Contains the account_id.

    Response:
        SuccessResponse: Returns the Account object if found.
        ErrorResponse: If the account does not exist.
    """
    response: SuccessResponse | ErrorResponse = account_use_case.get_account(get_schema.account_id)
    return to_lambda_http_response(response)


@deployable(
    [LAMBDA_TARGET],
    methods=["PATCH"],
    schema_cls=UpdateStatusAccountSchema,
    source="json",
    route="/accounts/update_status"
)
def update_status(update_status_schema: UpdateStatusAccountSchema):
    """
    Endpoint to update the status of an existing account.

    Supported Deployment Types:
        - Google Cloud Function
        - FastAPI

    HTTP Method:
        PATCH

    Route:
        fastapi: /accounts/update_status
        cloud-function: /update_status

    Request Body:
        UpdateStatusAccountSchema: Contains account_id, target status, and optional reason.

    Business Rules:
        - ACTIVE → SUSPENDED / CLOSED
        - SUSPENDED → ACTIVE / CLOSED
        - CLOSED → ❌ No transitions allowed.

    Response:
        SuccessResponse: If status update is successful.
        ErrorResponse: If validation fails or update is not allowed.
    """
    response: SuccessResponse | ErrorResponse = account_use_case.update_status(update_status_schema)
    return to_lambda_http_response(response)
