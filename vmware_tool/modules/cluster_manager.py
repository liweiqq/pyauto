from __future__ import annotations

from modules.vcenter_manager import VCenterSession


class ClusterManager:
    @staticmethod
    def ensure_cluster_exists(session: VCenterSession, cluster_name: str) -> None:
        clusters = session.discover_resources().get("clusters", [])
        if cluster_name not in clusters:
            raise ValueError(f"Cluster 不存在: {cluster_name}")
