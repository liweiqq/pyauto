#!/usr/bin/env python3
"""VMware vCenter 自动化运维平台 CLI 入口。"""

from __future__ import annotations

import argparse
from pathlib import Path

from modules.batch import BatchOperator
from modules.clone import CloneManager
from modules.config_loader import ConfigLoader
from modules.logging_utils import setup_logging
from modules.modify import VMModifyManager
from modules.password import PasswordManager
from modules.vcenter_manager import VCenterPool

BASE_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VMware 自动化运维平台")
    parser.add_argument("--config", default=str(BASE_DIR / "config" / "vcenter.yaml"))
    parser.add_argument("--templates", default=str(BASE_DIR / "config" / "templates.yaml"))
    parser.add_argument("--action", required=True, choices=["discover", "clone", "password", "modify", "batch"])
    parser.add_argument("--vcenter")
    parser.add_argument("--cluster")
    parser.add_argument("--template")
    parser.add_argument("--vm-name")
    parser.add_argument("--ip")
    parser.add_argument("--gateway")
    parser.add_argument("--dns", nargs="*")
    parser.add_argument("--hostname")
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--memory", type=int)
    parser.add_argument("--disk-gb", type=int)
    parser.add_argument("--target", help="密码变更目标主机/IP")
    parser.add_argument("--new-password")
    parser.add_argument("--batch-file", help="CSV/XLSX 文件")
    return parser


def main() -> None:
    setup_logging(BASE_DIR / "logs" / "platform.log")
    args = build_parser().parse_args()

    configs = ConfigLoader(args.config, args.templates)
    pool = VCenterPool(configs.vcenters)

    if args.action == "discover":
        info = pool.discover(args.vcenter)
        print(info)
        return

    clone_mgr = CloneManager(pool, configs.templates)
    pass_mgr = PasswordManager(pool)
    modify_mgr = VMModifyManager(pool)
    batch_mgr = BatchOperator(clone_mgr, pass_mgr, modify_mgr)

    if args.action == "clone":
        result = clone_mgr.clone_vm(
            vcenter_name=args.vcenter,
            cluster=args.cluster,
            template=args.template,
            vm_name=args.vm_name,
            ip=args.ip,
            gateway=args.gateway,
            dns=args.dns or [],
            hostname=args.hostname,
            cpu=args.cpu,
            memory_gb=args.memory,
            disk_gb=args.disk_gb,
        )
        print(result)
    elif args.action == "password":
        print(pass_mgr.change_password(args.vcenter, args.target, args.new_password))
    elif args.action == "modify":
        print(modify_mgr.modify_vm(args.vcenter, args.vm_name, args.cpu, args.memory, args.disk_gb))
    elif args.action == "batch":
        print(batch_mgr.run_batch(args.batch_file))


if __name__ == "__main__":
    main()
