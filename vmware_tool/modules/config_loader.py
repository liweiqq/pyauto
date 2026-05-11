from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ConfigLoader:
    vcenter_file: str
    templates_file: str

    @property
    def vcenters(self) -> dict[str, Any]:
        return self._load_yaml(self.vcenter_file).get("vcenters", {})

    @property
    def templates(self) -> dict[str, Any]:
        return self._load_yaml(self.templates_file).get("templates", {})

    @staticmethod
    def _load_yaml(path: str) -> dict[str, Any]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
