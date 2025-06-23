#!/usr/bin/env python3
"""
Auto-generate serverless.yml for AWS Lambda deployment using Serverless Framework.

Scans all functions decorated with @deployable(targets=[DeploymentTarget.LAMBDA])
and generates serverless.yml with correct handlers and HTTP event configs.

Requires:
- Your project structure must have Python modules inside 'src/application/routers'.
- Functions must use the @deployable decorator.
"""

import os
import sys
import inspect
import importlib.util
from pathlib import Path
import yaml

# Corrige path para importar os módulos da aplicação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utilities.frameworks.deployment_target import DeploymentTarget

USE_CASES_PATH = Path("src/application/routers")
BASE_FUNCTION_TEMPLATE = {
    "runtime": "python3.11",
    "memorySize": 512,
    "timeout": 30,
}


def import_module_from_path(module_name: str, path: Path):
    """Dynamically import a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def find_lambda_functions():
    functions = {}

    project_root = Path(__file__).resolve().parent.parent
    routers_path = project_root / USE_CASES_PATH

    for file in routers_path.rglob("*.py"):
        rel_path = file.relative_to(project_root)

        # Exemplo: src/application/routers/account_routers.py → src.application.routers.account_routers
        module_name = ".".join(rel_path.with_suffix("").parts)

        try:
            module = import_module_from_path(module_name, file)
        except Exception as e:
            print(f"⚠️ Error importing module '{module_name}': {e}")
            continue

        for name, func in inspect.getmembers(module, inspect.isfunction):
            targets = getattr(func, "_deploy_targets", None)
            if targets and DeploymentTarget.LAMBDA in targets:
                route = getattr(func, "_route", None)
                methods = getattr(func, "_methods", [])

                if not route or not methods:
                    print(f"⚠️ Function '{name}' missing route or methods. Skipping.")
                    continue

                functions[name] = {
                    "handler": f"{module_name.replace('.', '/')}.{name}",
                    "methods": methods,
                    "route": route,
                }

    return functions

def generate_serverless_yaml(lambda_functions):
    functions = {}

    for func_name, details in lambda_functions.items():
        function_config = {
            "handler": f"main.lambda_{func_name}",
            "events": [],
        }

        for method in details["methods"]:
            event = {
                "httpApi": {                      # mudou de "http" para "httpApi"
                    "path": details["route"],
                    "method": method.lower(),
                }
            }
            function_config["events"].append(event)

        functions[func_name] = function_config

    serverless_config = {
        "service": "account",  # seu serviço hardcoded como "account"
        "frameworkVersion": "3",
        "provider": {
            "name": "aws",
            "runtime": "python3.11",
            "region": "us-east-1",
            "environment": {
                "TARGET": "lambda",
                "ENVIRONMENT": "${env:ENVIRONMENT}",
            },
        },
        "plugins": [
            "serverless-python-requirements"
        ],
        "functions": functions,
        "custom": {
            "pythonRequirements": {
                "dockerizePip": True,
                "slim": True,
                "layer": False,
                "useStaticCache": True,
                "noDeploy": [],
            }
        }
    }

    return serverless_config


def main():
    print("🔎 Scanning for Lambda functions...")

    lambda_functions = find_lambda_functions()

    if not lambda_functions:
        print("🚨 No Lambda functions found.")
        sys.exit(1)

    print(f"✅ Found Lambda functions: {list(lambda_functions.keys())}")

    serverless_config = generate_serverless_yaml(lambda_functions)

    with open("serverless.yml", "w") as f:
        yaml.dump(serverless_config, f, sort_keys=False, default_flow_style=False)

    print("🎉 serverless.yml generated successfully!")


if __name__ == "__main__":
    main()
