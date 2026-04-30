# Stock Pilot（演示版）

一个仿 `stock.ossec.cn/tools` 风格的轻量股票工具站点，包含：

- 股票查询
- 暗盘信息
- 个股分析
- 暗盘历史
- 移动清单（本地收藏）

## 运行

直接用浏览器打开 `index.html` 即可，或用静态服务器：

```bash
python3 -m http.server 8080
```

然后访问 `http://127.0.0.1:8080/stock_web/`。

## 后续可扩展

- 接入真实行情 API（如 AkShare / Tushare / 券商 API）。
- 增加 K 线图、分时图、指标计算（MACD、RSI、布林带）。
- 增加用户登录与云端 watchlist 同步。
