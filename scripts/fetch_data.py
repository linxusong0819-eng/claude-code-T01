"""从东方财富公开行情接口抓取日线数据(前复权),保存为 CSV。

标的:
  - 龙净环保 600388.SH
  - 中证银行指数 399986
  - 中证红利指数 000922
  - 上证红利指数 000015
  - 沪深300 000300(对照基准)
"""
import json
import time
from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SECURITIES = {
    "longjing":   ("1.600388", "龙净环保"),
    "bank_index": ("0.399986", "中证银行指数"),
    "csi_div":    ("2.000922", "中证红利指数"),
    "sse_div":    ("1.000015", "上证红利指数"),
    "hs300":      ("1.000300", "沪深300"),
}

URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"


def fetch_kline(secid: str, beg: str = "20210101") -> pd.DataFrame:
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
        "klt": "101",   # 日线
        "fqt": "1",     # 前复权
        "beg": beg,
        "end": "20500101",
    }
    r = requests.get(URL, params=params, timeout=30,
                     headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    data = r.json()
    klines = (data.get("data") or {}).get("klines")
    if not klines:
        raise RuntimeError(f"no kline data for {secid}: {json.dumps(data)[:200]}")
    rows = [k.split(",") for k in klines]
    df = pd.DataFrame(rows, columns=[
        "date", "open", "close", "high", "low", "volume", "amount", "amplitude"])
    df["date"] = pd.to_datetime(df["date"])
    for c in ["open", "close", "high", "low", "volume", "amount", "amplitude"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    name = (data.get("data") or {}).get("name", "")
    print(f"  {secid} ({name}): {len(df)} bars, {df['date'].iloc[0].date()} ~ {df['date'].iloc[-1].date()}")
    return df


def main():
    for key, (secid, cname) in SECURITIES.items():
        print(f"fetching {cname} ...")
        last_err = None
        # 中证系指数在东财的市场前缀不固定,做候选回退
        candidates = [secid]
        code = secid.split(".")[1]
        for prefix in ("1", "2", "0"):
            alt = f"{prefix}.{code}"
            if alt not in candidates:
                candidates.append(alt)
        for sid in candidates:
            try:
                df = fetch_kline(sid)
                df.to_csv(DATA_DIR / f"{key}.csv", index=False)
                break
            except Exception as e:  # noqa: BLE001
                last_err = e
        else:
            raise SystemExit(f"failed to fetch {cname}: {last_err}")
        time.sleep(0.5)
    print("done.")


if __name__ == "__main__":
    main()
