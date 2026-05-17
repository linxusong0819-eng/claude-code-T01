# 阿尔法狂飙 ALPHA RUSH

90 秒操盘挑战 —— 前端游戏 + Node 后端全球排行榜。

## 运行

```bash
npm install
npm start
```

打开 http://localhost:3000 （手机访问用电脑局域网 IP，例如 http://192.168.x.x:3000）。

## 结构

- `public/index.html` — 前端：单文件游戏（行情引擎、K 线、做多做空、杠杆、连胜、移动端适配）
- `server.js` — 后端：Express，托管前端 + 排行榜 API
- `data/scores.json` — 成绩持久化（运行时自动生成，已 gitignore）

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/leaderboard?limit=10` | 取前 N 名（按净值排序）|
| POST | `/api/score` | 提交成绩，返回排名与 TOP 10 |

`POST /api/score` body：`{ name, equity, ret, sharpe, trades, win, maxDD }`，服务端做字段清洗与范围校验。

离线时游戏照常可玩，仅排行榜不可用。
