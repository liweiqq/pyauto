from __future__ import annotations


def bind_portgroup(vm_name: str, portgroup: str | None) -> str:
    if not portgroup:
        return f"{vm_name}: 使用默认 PortGroup"
    return f"{vm_name}: 已绑定 PortGroup={portgroup}"
