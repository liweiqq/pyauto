from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GuestCustomization:
    ip: str
    gateway: str
    dns: list[str]
    hostname: str

    def validate(self) -> None:
        if not all([self.ip, self.gateway, self.hostname]):
            raise ValueError("Guest 初始化参数缺失")
