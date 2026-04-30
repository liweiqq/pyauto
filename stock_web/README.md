# Stock Pilot（演示版）

一个仿 `stock.ossec.cn/tools` 风格的轻量股票工具站点，包含：

- 股票查询
- 暗盘信息
- 个股分析
- 暗盘历史
- 移动清单（本地收藏）

## 下载到本地运行

### 方式一：直接下载仓库 ZIP

1. 在代码托管页面点击 **Download ZIP**。
2. 解压后进入项目目录。
3. 打开终端执行：

```bash
cd pyauto/stock_web
./run_local.sh 8080
```

4. 浏览器打开：`http://127.0.0.1:8080`

### 方式二：使用 Git

```bash
git clone <你的仓库地址>
cd pyauto/stock_web
./run_local.sh 8080
```


### 方式三：Windows（CMD / PowerShell）

1. 下载并安装 Python（安装时勾选 `Add python.exe to PATH`）。
2. 打开 `cmd` 或 PowerShell，进入目录：

```powershell
cd pyauto\stock_web
```

3. 启动：

```powershell
run_local.bat 8080
```

4. 浏览器访问：`http://127.0.0.1:8080`

如果你不想用 `.bat`，也可以直接执行：

```powershell
python -m http.server 8080
```

## 不使用脚本的运行方式

```bash
cd stock_web
python3 -m http.server 8080
```

## 常见问题

- 如果端口 8080 被占用：

```bash
./run_local.sh 9000
```

- 页面数据是演示数据：
  当前 `app.js` 内置了示例股票与暗盘数据，可按需替换为真实 API。

## 当前行为说明

- 搜索未收录股票时，会自动生成该代码的模拟数据，避免页面中断。

## 后续可扩展

- 接入真实行情 API（如 AkShare / Tushare / 券商 API）。
- 增加 K 线图、分时图、指标计算（MACD、RSI、布林带）。
- 增加用户登录与云端 watchlist 同步。
