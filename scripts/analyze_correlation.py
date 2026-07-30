# -*- coding: utf-8 -*-
"""龙净环保 vs 银行板块 / 红利指数 关联度分析。

读取 data/*.csv(由 fetch_data.py 生成),计算:
  1. 日收益率 Pearson 相关系数(全样本 / 近1年 / 近半年)
  2. 周收益率相关系数(降低日内噪音)
  3. 60 日滚动相关系数序列及走势图
  4. 龙净环保对各指数的 Beta 与 R²
输出 reports/correlation_report.md 与 reports/rolling_corr.png。
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

NAMES = {
    "longjing": "龙净环保",
    "bank_index": "中证银行指数",
    "csi_div": "中证红利指数",
    "sse_div": "上证红利指数",
    "hs300": "沪深300",
}


def load_closes() -> pd.DataFrame:
    frames = {}
    for key, cname in NAMES.items():
        f = DATA_DIR / f"{key}.csv"
        if not f.exists():
            print(f"warn: missing {f}, skip {cname}")
            continue
        df = pd.read_csv(f, parse_dates=["date"])
        frames[cname] = df.set_index("date")["close"]
    closes = pd.DataFrame(frames).dropna()
    return closes


def corr_table(rets: pd.DataFrame, target: str) -> pd.Series:
    return rets.corr()[target].drop(target)


def beta_r2(y: pd.Series, x: pd.Series):
    cov = np.cov(y, x)
    beta = cov[0, 1] / cov[1, 1]
    r = np.corrcoef(y, x)[0, 1]
    return beta, r ** 2


def main():
    closes = load_closes()
    target = NAMES["longjing"]
    if target not in closes.columns:
        raise SystemExit("缺少龙净环保数据,请先运行 fetch_data.py")

    daily = closes.pct_change().dropna()
    weekly = closes.resample("W-FRI").last().pct_change().dropna()

    end = daily.index.max()
    win_1y = daily[daily.index >= end - pd.DateOffset(years=1)]
    win_6m = daily[daily.index >= end - pd.DateOffset(months=6)]

    lines = []
    lines.append("# 龙净环保 与 银行板块 / 红利指数 关联度分析\n")
    lines.append(f"样本区间:{closes.index.min().date()} ~ {closes.index.max().date()},"
                 f"共 {len(closes)} 个交易日;收益率为前复权收盘价计算。\n")

    lines.append("## 1. 日收益率相关系数(Pearson)\n")
    tbl = pd.DataFrame({
        "全样本": corr_table(daily, target),
        "近1年": corr_table(win_1y, target),
        "近半年": corr_table(win_6m, target),
    }).round(3)
    lines.append(tbl.to_markdown() + "\n")

    lines.append("## 2. 周收益率相关系数(全样本)\n")
    wtbl = corr_table(weekly, target).round(3).to_frame("周收益相关")
    lines.append(wtbl.to_markdown() + "\n")

    lines.append("## 3. Beta 与 R²(全样本日收益)\n")
    rows = []
    for col in daily.columns:
        if col == target:
            continue
        b, r2 = beta_r2(daily[target], daily[col])
        rows.append({"指数": col, "Beta": round(b, 3), "R²": round(r2, 3)})
    lines.append(pd.DataFrame(rows).set_index("指数").to_markdown() + "\n")

    lines.append("## 4. 指数间相关(参照)\n")
    lines.append(daily.corr().round(3).to_markdown() + "\n")

    roll = pd.DataFrame({
        col: daily[target].rolling(60).corr(daily[col])
        for col in daily.columns if col != target
    }).dropna(how="all")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
        for fp in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                   "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
            if Path(fp).exists():
                font_manager.fontManager.addfont(fp)
                plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
                break
        plt.rcParams["axes.unicode_minus"] = False
        fig, ax = plt.subplots(figsize=(11, 5))
        for col in roll.columns:
            ax.plot(roll.index, roll[col], label=col, linewidth=1.2)
        ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
        ax.set_title("龙净环保 60日滚动相关系数")
        ax.set_ylim(-1, 1)
        ax.legend()
        fig.tight_layout()
        fig.savefig(REPORT_DIR / "rolling_corr.png", dpi=150)
        lines.append("## 5. 60日滚动相关系数\n\n![rolling](rolling_corr.png)\n")
    except Exception as e:  # noqa: BLE001
        print(f"warn: chart skipped ({e})")

    stats = roll.agg(["min", "max", "mean"]).round(3)
    lines.append("滚动相关统计:\n")
    lines.append(stats.to_markdown() + "\n")

    out = REPORT_DIR / "correlation_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"report written to {out}")


if __name__ == "__main__":
    main()
