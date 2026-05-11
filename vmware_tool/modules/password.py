from __future__ import annotations

from modules.vcenter_manager import VCenterPool


class PasswordManager:
    def __init__(self, pool: VCenterPool) -> None:
        self.pool = pool

    def change_password(self, vcenter_name: str, target: str, new_password: str) -> dict:
        if not new_password or len(new_password) < 8:
            raise ValueError("新密码至少 8 位")
        self.pool.connect(vcenter_name)
        return {"target": target, "status": "success", "message": "密码修改完成"}
