"""Handling secrets (i.e., API keys)."""

from pathlib import Path

import yaml
from pydantic import BaseModel


class ApiKeys(BaseModel):
    """API keys."""

    tavily: str


class Secrets(BaseModel):
    """Secrets data structure."""

    api_keys: ApiKeys


def load_secrets(secrets_yaml: Path = Path("./secrets.yaml")) -> Secrets:
    """Load secrets from file.

    Args:
        secrets_yaml (Path, optional): Secrets YAML file. Defaults to "./secrets.yaml".

    Returns:
        Secrets: Validated data structure with all secrets.

    """
    with secrets_yaml.open() as f:
        return Secrets(**yaml.safe_load(f))
