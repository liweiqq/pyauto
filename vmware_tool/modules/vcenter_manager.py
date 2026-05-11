from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VCenterSession:
    name: str
    config: dict[str, Any]

    def discover_resources(self) -> dict[str, Any]:
        return {
            "vcenter": self.name,
            "datacenter": self.config.get("datacenter"),
            "clusters": ["Cluster-A", "Cluster-B"],
            "resource_pools": ["RP-Default"],
            "datastores": ["Datastore-1"],
            "portgroups": ["VM Network"],
            "templates": ["centos7-template", "win2019-template"],
        }


class VCenterPool:
    def __init__(self, vcenters: dict[str, Any]) -> None:
        self._configs = vcenters
        self._sessions: dict[str, VCenterSession] = {}

    def connect(self, name: str) -> VCenterSession:
        if not name:
            raise ValueError("必须指定 vCenter 名称")
        if name not in self._configs:
            raise KeyError(f"未知 vCenter: {name}")
        if name not in self._sessions:
            logger.info("创建 vCenter 会话: %s", name)
            self._sessions[name] = VCenterSession(name=name, config=self._configs[name])
        return self._sessions[name]

    def discover(self, name: str | None) -> dict[str, Any]:
        if name:
            return self.connect(name).discover_resources()
        return {vc: self.connect(vc).discover_resources() for vc in self._configs}
