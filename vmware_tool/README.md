# VMware vCenter 自动化运维平台（Python）

## 快速开始

```bash
python main.py --action discover
python main.py --action clone --vcenter prod-vcenter --cluster Cluster-A --template centos7-template --vm-name vm-demo --ip 10.0.0.20 --gateway 10.0.0.1 --hostname vm-demo
python main.py --action password --vcenter prod-vcenter --target 10.0.0.20 --new-password 'NewPassw0rd!'
python main.py --action modify --vcenter prod-vcenter --vm-name vm-demo --cpu 4 --memory 8 --disk-gb 100
```

## 功能实现说明

- 多 vCenter 配置与连接池复用
- 资源动态发现（datacenter/cluster/resource pool/datastore/network/template）
- 虚拟机克隆与 Guest 初始化参数校验
- 密码修改（IP/主机名）
- CPU/内存/磁盘扩容修改
- 批量 CSV/XLSX 导入
- 审计日志输出到 `logs/platform.log`
