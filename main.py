import os

from utilities.frameworks.handler_resolver import HandlerResolver
from utilities.logger.log_utils import Logger
from utilities.logger.logail_handler import LogtailHandler

from src.application import routers
from src.config.custom_config import ENVIRONMENT

TARGET = os.environ.get("TARGET", "lambda")

resolver = HandlerResolver(routers, TARGET)
app_or_functions = resolver.get_handler()

Logger.setup(LogtailHandler(), ENVIRONMENT.log_level)

if TARGET == "fastapi":
    import uvicorn
    uvicorn.run(app_or_functions, host="0.0.0.0", port=8080)
elif TARGET == "cloudfunction":
    function_create_account = app_or_functions["create_account"]
    function_get_account = app_or_functions["get_account"]
    function_update_status = app_or_functions["update_status"]
elif TARGET == "lambda":
    lambda_create_account = app_or_functions["create_account"]
    lambda_get_account = app_or_functions["get_account"]
    lambda_update_status = app_or_functions["update_status"]