from utilities.cross_cutting.application.routers.http_response_adapter import to_gcp_http_response
from utilities.cross_cutting.application.schemas.responses_schema import SuccessResponse, ErrorResponse
from utilities.depency_injections.injection_manager import InjectionManager

from utilities.frameworks.deployment_decorator import deployable

from src.application.schemas.acchount_schema import AccountSchema, GetAccountSchema, UpdateStatusAccountSchema
from src.config.dependency_start import start_account_dependencies
from src.application.use_cases.account_use_case import AccountUseCase

start_account_dependencies()

account_use_case = InjectionManager.get_dependency(AccountUseCase)


@deployable(["cloudfunction", "fastapi"], methods=["POST"], schema_cls=AccountSchema, source="json", route="/accounts/create")
def create_account(account_schema: AccountSchema):
    """
    Create a new account.
    """
    response: SuccessResponse | ErrorResponse  = account_use_case.create_account(account_schema)
    return to_gcp_http_response(response)

@deployable(["cloudfunction", "fastapi"], methods=["GET"], schema_cls=GetAccountSchema, source="args", route="/accounts/get")
def get_account(get_schema: GetAccountSchema):
    """
    Get account by ID.
    """
    response: SuccessResponse | ErrorResponse  = account_use_case.get_account(get_schema.account_id)
    return to_gcp_http_response(response)


@deployable(["cloudfunction", "fastapi"], methods=["PATCH"], schema_cls=UpdateStatusAccountSchema, source="json", route="/accounts/update_status")
def update_status(update_status_schema: UpdateStatusAccountSchema):
    """
    Update the status of an account.
    """
    response: SuccessResponse | ErrorResponse = account_use_case.update_status(update_status_schema)
    return to_gcp_http_response(response)
