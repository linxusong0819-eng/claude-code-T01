# 龙净环保 × 银行板块 × 红利指数 关联度分析

## 标的

| 标的 | 代码 | 说明 |
|---|---|---|
| 龙净环保 | 600388.SH | 大气治理环保设备龙头,紫金矿业控股 |
| 中证银行指数 | 399986 | 银行板块代表 |
| 中证红利指数 | 000922 | 红利风格代表 |
| 上证红利指数 | 000015 | 红利风格(沪市) |
| 沪深300 | 000300 | 市场基准(对照) |

## 使用方法

```bash
pip install -r requirements.txt
python scripts/fetch_data.py          # 抓取前复权日线(东方财富公开接口)
python scripts/analyze_correlation.py # 生成 reports/correlation_report.md 及滚动相关走势图
```

## 分析口径

- 前复权收盘价计算日/周收益率;
- Pearson 相关系数:全样本、近 1 年、近半年三个窗口;
- 60 日滚动相关系数观察关联度的时变特征;
- Beta 与 R² 衡量龙净环保对各指数的敏感度与解释力;
- 指数间相关矩阵作为参照(银行板块与红利指数本身高度相关,银行是中证红利的第一大权重行业)。

## 运行环境注意

云端沙箱会话若出网策略未放行 `*.eastmoney.com` 等行情域名,`fetch_data.py`
会因代理 403 失败;请在允许外网的环境运行,或将行情 CSV(列:date,close)
手工放入 `data/` 目录后直接运行分析脚本。CSV 文件名约定:
`longjing.csv`、`bank_index.csv`、`csi_div.csv`、`sse_div.csv`、`hs300.csv`。
