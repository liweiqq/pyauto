#!/usr/bin/env python3
"""克隆 vSphere 模板/虚拟机，并可在 Guest 内执行网络与主机名初始化。"""

import argparse
import atexit
import base64
import importlib
import importlib.util
import ipaddress
import socket
import ssl
import time
from dataclasses import dataclass
from typing import Optional

VCENTER = "10.105.0.110"
USERNAME = "administrator@vsphere.local"
PASSWORD = "Asd.12345"
TEMPLATE_NAME = "Windows_Server_2025_20260423"
DEFAULT_VM_NAME = "win2025-001"
CLUSTER_NAME = "VSAN-Cluster02"
DATASTORE = "vsanDatastore -Cluster02"
FOLDER = "vm"
DEFAULT_IP = "10.105.100.184"
DEFAULT_MASK = 24
DEFAULT_GATEWAY = "10.105.100.254"
DEFAULT_DNS = "10.105.0.230"
DEFAULT_GUEST_USER = "Administrator"
DEFAULT_GUEST_PASS = "Jiyu1212"
WAIT_TIMEOUT = 900
POLL_INTERVAL = 5

connect = None
vim = None


@dataclass
class RuntimeConfig:
    vm_name: str
    source_template: Optional[str]
    source_vm: Optional[str]
    ip: str
    mask: int
    gateway: str
    dns: str
    cpu: int
    memory_gb: int
    guest_user: Optional[str]
    guest_pass: Optional[str]
    set_hostname: bool


def log(msg: str):
    print(msg, flush=True)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--vm-name", default=DEFAULT_VM_NAME)
    p.add_argument("--source-template", default=None)
    p.add_argument("--source-vm", default=None)
    p.add_argument("--ip", default=DEFAULT_IP)
    p.add_argument("--mask", default=str(DEFAULT_MASK))
    p.add_argument("--gateway", default=DEFAULT_GATEWAY)
    p.add_argument("--dns", default=DEFAULT_DNS)
    p.add_argument("--cpu", type=int, default=4)
    p.add_argument("--memory-gb", type=int, default=8)
    p.add_argument("--with-network-init", action="store_true")
    p.add_argument("--guest-user", default=None)
    p.add_argument("--guest-pass", default=None)
    p.add_argument("--set-hostname", action="store_true", help="克隆后在 Guest 内将主机名改为 --vm-name")
    return p.parse_args()


def load_pyvmomi():
    if importlib.util.find_spec("pyVim") is None or importlib.util.find_spec("pyVmomi") is None:
        raise SystemExit("[x] 缺少依赖 pyvmomi")
    pyvim_connect = importlib.import_module("pyVim.connect")
    pyvmomi_pkg = importlib.import_module("pyVmomi")
    return pyvim_connect, pyvmomi_pkg.vim


def wait_for_task(task):
    start = time.time()
    while task.info.state in (vim.TaskInfo.State.running, vim.TaskInfo.State.queued):
        if time.time() - start > WAIT_TIMEOUT:
            raise TimeoutError("task timeout")
        time.sleep(POLL_INTERVAL)
    if task.info.state != vim.TaskInfo.State.success:
        raise RuntimeError(task.info.error)
    return task.info.result


def get_obj(content, vimtype, name):
    view = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    try:
        for obj in view.view:
            if obj.name == name:
                return obj
    finally:
        view.Destroy()
    return None


def connect_vcenter():
    with socket.create_connection((VCENTER, 443), timeout=15):
        pass
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    si = connect.SmartConnect(host=VCENTER, user=USERNAME, pwd=PASSWORD, sslContext=ctx)
    atexit.register(connect.Disconnect, si)
    return si, si.RetrieveContent()


def resolve_source_vm(content, cfg):
    if cfg.source_template and cfg.source_vm:
        raise ValueError("--source-template 与 --source-vm 不能同时指定")
    if cfg.source_vm:
        vm_obj = get_obj(content, [vim.VirtualMachine], cfg.source_vm)
        if not vm_obj:
            raise ValueError(f"未找到源虚拟机: {cfg.source_vm}")
        return vm_obj
    template_name = cfg.source_template or TEMPLATE_NAME
    vm_obj = get_obj(content, [vim.VirtualMachine], template_name)
    if not vm_obj:
        raise ValueError(f"未找到模板: {template_name}")
    return vm_obj


def clone_vm(content, cfg):
    src = resolve_source_vm(content, cfg)
    datastore = get_obj(content, [vim.Datastore], DATASTORE)
    folder = get_obj(content, [vim.Folder], FOLDER)
    pool = src.resourcePool or get_obj(content, [vim.ClusterComputeResource], CLUSTER_NAME).resourcePool
    relocate = vim.vm.RelocateSpec(datastore=datastore, pool=pool)
    spec = vim.vm.ConfigSpec(numCPUs=cfg.cpu, memoryMB=cfg.memory_gb * 1024)
    clone_spec = vim.vm.CloneSpec(powerOn=True, template=False, location=relocate, config=spec)
    vm = wait_for_task(src.Clone(folder=folder, name=cfg.vm_name, spec=clone_spec))
    return vm


def wait_guest_ops_ready(vm):
    start = time.time()
    while time.time() - start < WAIT_TIMEOUT:
        vm.Reload()
        if vm.guest.toolsRunningStatus == "guestToolsRunning" and getattr(vm.guest, "guestOperationsReady", False):
            return
        time.sleep(POLL_INTERVAL)
    raise TimeoutError("guest ops not ready")


def auth_candidates(cfg):
    candidates = []
    if cfg.guest_user and cfg.guest_pass:
        u = cfg.guest_user
        candidates += [u, u.lower(), u.capitalize(), f".\\{u.split('\\')[-1]}"]
        dedup = []
        seen = set()
        for x in candidates:
            if x not in seen:
                seen.add(x)
                dedup.append((x, cfg.guest_pass))
        return dedup
    return [
        (DEFAULT_GUEST_USER, DEFAULT_GUEST_PASS),
        ("administrator", DEFAULT_GUEST_PASS),
        (r".\Administrator", DEFAULT_GUEST_PASS),
    ]


def run_program(si, vm, program, arguments, cfg):
    wait_guest_ops_ready(vm)
    pm = si.content.guestOperationsManager.processManager
    last_err = None
    for user, pw in auth_candidates(cfg):
        auth = vim.vm.guest.NamePasswordAuthentication(username=user, password=pw)
        try:
            pid = pm.StartProgramInGuest(vm=vm, auth=auth, spec=vim.vm.guest.ProcessManager.ProgramSpec(programPath=program, arguments=arguments))
            log(f"[+] Guest 认证成功: {user}, PID={pid}")
            return pm, auth, pid
        except vim.fault.InvalidGuestLogin as exc:
            last_err = exc
            log(f"[!] Guest 认证失败: {user}")
    raise RuntimeError(f"Guest 认证全部失败: {last_err}")


def wait_pid(pm, vm, auth, pid):
    start = time.time()
    while time.time() - start < WAIT_TIMEOUT:
        proc = pm.ListProcessesInGuest(vm=vm, auth=auth, pids=[pid])
        if proc and proc[0].endTime:
            if proc[0].exitCode == 0:
                return
            raise RuntimeError(f"guest process failed: {proc[0].exitCode}")
        time.sleep(POLL_INTERVAL)
    raise TimeoutError("wait process timeout")


def configure_network(si, vm, cfg):
    script = f"""
$adapter = Get-NetAdapter | ? {{$_.Status -eq 'Up'}} | select -First 1
if (-not $adapter) {{ throw 'No active network adapter found' }}
Get-NetIPAddress -InterfaceAlias $adapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
Get-NetRoute -InterfaceAlias $adapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetRoute -Confirm:$false -ErrorAction SilentlyContinue
New-NetIPAddress -InterfaceAlias $adapter.Name -IPAddress '{cfg.ip}' -PrefixLength {cfg.mask} -DefaultGateway '{cfg.gateway}'
Set-DnsClientServerAddress -InterfaceAlias $adapter.Name -ServerAddresses '{cfg.dns}'
""".strip()
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    args = f"-NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand {encoded}"
    pm, auth, pid = run_program(si, vm, r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", args, cfg)
    wait_pid(pm, vm, auth, pid)


def set_guest_hostname(si, vm, cfg):
    cmd = f"-NoProfile -NonInteractive -Command \"Rename-Computer -NewName '{cfg.vm_name}' -Force -Restart\""
    pm, auth, pid = run_program(si, vm, r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", cmd, cfg)
    try:
        wait_pid(pm, vm, auth, pid)
    except Exception:
        pass
    # wait reboot + hostname
    start = time.time()
    while time.time() - start < WAIT_TIMEOUT * 2:
        vm.Reload()
        name = (getattr(vm.guest, "hostName", "") or "").split(".")[0].lower()
        if name == cfg.vm_name.lower():
            return
        time.sleep(POLL_INTERVAL)


def main():
    global connect, vim
    args = parse_args()
    connect, vim = load_pyvmomi()
    cfg = RuntimeConfig(
        vm_name=args.vm_name,
        source_template=args.source_template,
        source_vm=args.source_vm,
        ip=args.ip,
        mask=ipaddress.ip_network(f"0.0.0.0/{args.mask}", strict=False).prefixlen,
        gateway=args.gateway,
        dns=args.dns,
        cpu=args.cpu,
        memory_gb=args.memory_gb,
        guest_user=args.guest_user,
        guest_pass=args.guest_pass,
        set_hostname=args.set_hostname,
    )
    si, content = connect_vcenter()
    vm = clone_vm(content, cfg)
    if args.with_network_init:
        configure_network(si, vm, cfg)
    if cfg.set_hostname:
        set_guest_hostname(si, vm, cfg)


if __name__ == "__main__":
    main()
