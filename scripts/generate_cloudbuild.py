#!/usr/bin/env python3

import os
import sys
import inspect
import importlib.util
from pathlib import Path
import yaml

# Caminho base para os use_cases
USE_CASES_PATH = "src/application/routers"

BASE_YAML_STEP = {
    "name": "gcr.io/cloud-builders/gcloud",
    "args": [],
}

# Novo step para gerar o requirements.txt com o token
GENERATE_REQUIREMENTS_STEP = {
    "name": "gcr.io/cloud-builders/gcloud",
    "id": "Generate requirements.txt",
    "entrypoint": "bash",
    "args": [
        "-c",
        """
        echo "🔧 Atualizando requirements.txt com token privado..."
        # Garante que o arquivo termina com newline para evitar concatenação errada
        sed -i -e '$a\\' requirements.txt
        # Remove linha antiga da lib privada (se existir)
        sed -i '/git+https:\\/\\/github.com\\/LuizHenrique78\\/utilities.git/d' requirements.txt
        # Adiciona a linha com token
        echo "git+https://${_GITHUB_TOKEN}@github.com/LuizHenrique78/utilities.git@1.0.2#egg=utilities" >> requirements.txt
        """
    ],
}



def import_module_from_path(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def find_cloudfunction_methods():
    cloud_functions = set()  # Usando set para evitar duplicatas

    for file in Path(USE_CASES_PATH).rglob("*.py"):
        module_name = (
            str(file)
            .replace("/", ".")
            .replace("\\", ".")
            .replace(".py", "")
        )

        module = import_module_from_path(module_name, file)

        for name, obj in inspect.getmembers(module, inspect.isfunction):
            targets = getattr(obj, "_deploy_targets", [])
            if "cloudfunction" in targets:
                cloud_functions.add(name)  # Apenas o nome

    return list(cloud_functions)

def generate_cloudbuild_yaml(cloud_functions, region="us-central1"):
    steps = []

    # Adiciona o step para gerar o requirements.txt
    steps.append(GENERATE_REQUIREMENTS_STEP)

    # Mapeamento manual para definir qual trigger usar
    trigger_mapping = {
        "main": {
            "trigger": "--trigger-topic=transactions.incoming"
        },
        "callback": {
            "trigger": "--trigger-topic=transactions.incoming"
        },
        "enqueue_message": {
            "trigger": "--trigger-topic=transactions.incoming"
        },
        "process_batch": {
            "trigger": "--trigger-topic=transactions.incoming"
        },
        # Adicione outros se quiser usar triggers HTTP para outras funções
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

        # Se for HTTP, permite acesso público
        if trigger["trigger"] == "--trigger-http":
            step["args"].append("--allow-unauthenticated")

        steps.append(step)

    cloudbuild_yaml = {
        "steps": steps,
        "options": {
            "logging": "CLOUD_LOGGING_ONLY"
        }
    }
    return cloudbuild_yaml

def main():
    print("🔍 Procurando funções decoradas com @deployable('cloudfunction')...")
    cloud_functions = find_cloudfunction_methods()

    if not cloud_functions:
        print("🚨 Nenhuma função encontrada.")
        return

    print(f"✅ Funções encontradas: {cloud_functions}")

    cloudbuild_config = generate_cloudbuild_yaml(cloud_functions)

    output_file = "cloudbuild.yaml"
    with open(output_file, "w") as f:
        yaml.dump(cloudbuild_config, f, sort_keys=False, default_flow_style=False)

    print(f"🎉 Arquivo '{output_file}' gerado com sucesso!")

if __name__ == "__main__":
    main()
