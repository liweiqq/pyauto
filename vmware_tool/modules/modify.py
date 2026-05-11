from __future__ import annotations

from modules.vcenter_manager import VCenterPool


class VMModifyManager:
    def __init__(self, pool: VCenterPool) -> None:
        self.pool = pool

    def modify_vm(self, vcenter_name: str, vm_name: str, cpu: int | None, memory_gb: int | None,
                  disk_gb: int | None) -> dict:
        self.pool.connect(vcenter_name)
        if not vm_name:
            raise ValueError("必须指定 VM 名称")
        return {
            "vm_name": vm_name,
            "status": "success",
            "changes": {"cpu": cpu, "memory_gb": memory_gb, "disk_expand_gb": disk_gb},
        }
