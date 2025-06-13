import os

from utilities.frameworks.handler_resolver import HandlerResolver
from src.application import routers  # seu pacote de rotas
TARGET = os.environ.get("TARGET", "fastapi")  # ou "fastapi")

resolver = HandlerResolver(routers, TARGET)
app_or_functions = resolver.get_handler()

if TARGET == "fastapi":
    import uvicorn
    uvicorn.run(app_or_functions, host="0.0.0.0", port=8080)
else:
    # Exemplo, expor funções para CloudFunction
    function_create_account = app_or_functions["create_account"]
    function_get_account = app_or_functions["get_account"]
