#!/usr/bin/env python3
"""
Script for automatically generating a cloudbuild.yaml file for deploying Google Cloud Functions.

What it does:

1. Scans the project for functions decorated with `@deployable(targets=["cloudfunction"])`.
2. Generates Cloud Build steps for deploying each Cloud Function.
3. Adds a step to update the `requirements.txt` with a private GitHub token for private dependency installation.
4. Outputs the final result as `cloudbuild.yaml`.

Requirements:
- Project directory structure with Python modules under `src/application/routers`.
- Functions must use the `@deployable` decorator to be detected.
"""

import os
import sys
import inspect
import importlib.util
from pathlib import Path
import yaml

# Base path where use case routers are located
USE_CASES_PATH = "src/application/routers"

# Base YAML step for Cloud Build deploy
BASE_YAML_STEP = {
    "name": "gcr.io/cloud-builders/gcloud",
    "args": [],
}

# Step for updating requirements.txt with GitHub token for private repo
GENERATE_REQUIREMENTS_STEP = {
    "name": "gcr.io/cloud-builders/gcloud",
    "id": "Generate requirements.txt",
    "entrypoint": "bash",
    "args": [
        "-c",
        """
        echo "🔧 Updating requirements.txt with private token..."
        sed -i -e '$a\\' requirements.txt
        sed -i '/git+https:\\/\\/github.com\\/LuizHenrique78\\/utilities.git/d' requirements.txt
        echo "git+https://${_GITHUB_TOKEN}@github.com/LuizHenrique78/utilities.git@1.0.2#egg=utilities" >> requirements.txt
        """
    ],
}


def import_module_from_path(module_name: str, path: Path):
    """
    Dynamically import a Python module from a file path.

    Args:
        module_name (str): Desired module name for Python system modules.
        path (Path): Absolute path to the Python file.

    Returns:
        module: The imported Python module.
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def find_cloudfunction_methods() -> list[str]:
    """
    Find all Python functions decorated with `@deployable(targets=["cloudfunction"])`.

    Returns:
        list[str]: List of function names detected for deployment.
    """
    cloud_functions = set()

    for file in Path(USE_CASES_PATH).rglob("*.py"):
        module_name = str(file).replace("/", ".").replace("\\", ".").replace(".py", "")
        try:
            module = import_module_from_path(module_name, file)
        except Exception as e:
            print(f"⚠️ Error importing module '{module_name}': {e}")
            continue

        for name, obj in inspect.getmembers(module, inspect.isfunction):
            targets = getattr(obj, "_deploy_targets", [])
            if "cloudfunction" in targets:
                cloud_functions.add(name)

    return list(cloud_functions)


def generate_cloudbuild_yaml(cloud_functions: list[str], region: str = "us-central1") -> dict:
    """
    Generate the structure for the cloudbuild.yaml file with deployment steps for each Cloud Function.

    Args:
        cloud_functions (list[str]): List of function names to deploy.
        region (str): GCP region for deployment.

    Returns:
        dict: Dictionary ready to be serialized as YAML.
    """
    steps = [GENERATE_REQUIREMENTS_STEP]

    # Optional: manual trigger mapping by function name
    trigger_mapping = {
        "main": {"trigger": "--trigger-topic=transactions.incoming"},
        "callback": {"trigger": "--trigger-topic=transactions.incoming"},
        "enqueue_message": {"trigger": "--trigger-topic=transactions.incoming"},
        "process_batch": {"trigger": "--trigger-topic=transactions.incoming"},
        # Others will default to HTTP trigger
    }

    for func_name in cloud_functions:
        step = dict(BASE_YAML_STEP)
        step["id"] = f"Deploy {func_name}"
        trigger = trigger_mapping.get(func_name, {"trigger": "--trigger-http"})

        step["args"] = [
            "functions", "deploy", func_name,
            f"--region={region}",
            "--runtime=python311",
            "--source=.",
            f"--entry-point=function_{func_name}",
            trigger["trigger"],
            "--set-env-vars=TARGET=cloudfunction",
            "--timeout=540s",
        ]

        # If it's an HTTP-triggered function, allow public access
        if trigger["trigger"] == "--trigger-http":
            step["args"].append("--allow-unauthenticated")

        steps.append(step)

    return {
        "steps": steps,
        "options": {
            "logging": "CLOUD_LOGGING_ONLY"
        }
    }


def main():
    """
    Main execution function.
    Responsible for scanning functions and generating the cloudbuild.yaml file.
    """
    print("🔍 Searching for functions with target 'cloudfunction'...")

    cloud_functions = find_cloudfunction_methods()

    if not cloud_functions:
        print("🚨 No functions with target 'cloudfunction' found.")
        sys.exit(1)

    print(f"✅ Functions found: {cloud_functions}")

    cloudbuild_config = generate_cloudbuild_yaml(cloud_functions)

    output_file = "cloudbuild.yaml"
    with open(output_file, "w") as f:
        yaml.dump(cloudbuild_config, f, sort_keys=False, default_flow_style=False)

    print(f"🎉 File '{output_file}' generated successfully!")


if __name__ == "__main__":
    main()
