from __future__ import annotations

from dataclasses import asdict, dataclass

from modules.cluster_manager import ClusterManager
from modules.network import bind_portgroup
from modules.vm_guest import GuestCustomization
from modules.vcenter_manager import VCenterPool


@dataclass
class CloneResult:
    vm_name: str
    status: str
    detail: dict


class CloneManager:
    def __init__(self, pool: VCenterPool, templates: dict) -> None:
        self.pool = pool
        self.templates = templates

    def clone_vm(self, vcenter_name: str, cluster: str, template: str, vm_name: str, ip: str,
                 gateway: str, dns: list[str], hostname: str, cpu: int | None = None,
                 memory_gb: int | None = None, disk_gb: int | None = None,
                 portgroup: str | None = None) -> dict:
        session = self.pool.connect(vcenter_name)
        ClusterManager.ensure_cluster_exists(session, cluster)
        if template not in self.templates:
            raise ValueError(f"模板不存在: {template}")

        guest = GuestCustomization(ip=ip, gateway=gateway, dns=dns, hostname=hostname)
        guest.validate()
        net_msg = bind_portgroup(vm_name, portgroup)

        result = CloneResult(
            vm_name=vm_name,
            status="success",
            detail={
                "vcenter": vcenter_name,
                "cluster": cluster,
                "template": template,
                "cpu": cpu,
                "memory_gb": memory_gb,
                "disk_gb": disk_gb,
                "guest": asdict(guest),
                "network": net_msg,
                "power_on": True,
            },
        )
        return asdict(result)
