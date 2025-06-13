from utilities.environment import EnvConfig, Environment


class CustomConfig(EnvConfig):
    ...


ENVIRONMENT = CustomConfig(environment=Environment.DEVELOPMENT)