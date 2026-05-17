"use strict";
const express = require("express");
const path = require("path");
const fs = require("fs");

const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, "data");
const SCORES_FILE = path.join(DATA_DIR, "scores.json");
const MAX_SCORES = 500;

const app = express();
app.use(express.json({ limit: "8kb" }));
app.use(express.static(path.join(__dirname, "public")));

function readScores() {
  try {
    return JSON.parse(fs.readFileSync(SCORES_FILE, "utf8"));
  } catch {
    return [];
  }
}

function writeScores(list) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const tmp = SCORES_FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(list));
  fs.renameSync(tmp, SCORES_FILE);
}

function cleanName(v) {
  return String(v == null ? "" : v)
    .replace(/[<>&"'`]/g, "")
    .trim()
    .slice(0, 16) || "匿名操盘手";
}

function num(v, lo, hi) {
  const n = Number(v);
  if (!Number.isFinite(n)) return null;
  return Math.min(hi, Math.max(lo, n));
}

app.get("/api/leaderboard", (req, res) => {
  const limit = Math.min(50, Math.max(1, parseInt(req.query.limit, 10) || 10));
  const top = readScores()
    .sort((a, b) => b.equity - a.equity)
    .slice(0, limit);
  res.json(top);
});

app.post("/api/score", (req, res) => {
  const b = req.body || {};
  const equity = num(b.equity, 0, 1e9);
  const ret = num(b.ret, -100, 1e6);
  if (equity === null || ret === null) {
    return res.status(400).json({ error: "invalid score" });
  }
  const entry = {
    name: cleanName(b.name),
    equity: Math.round(equity),
    ret: Math.round(ret * 10) / 10,
    sharpe: num(b.sharpe, -50, 50) ?? 0,
    trades: Math.round(num(b.trades, 0, 1e4) ?? 0),
    win: Math.round(num(b.win, 0, 100) ?? 0),
    maxDD: Math.round((num(b.maxDD, 0, 100) ?? 0) * 10) / 10,
    ts: Date.now(),
  };
  const list = readScores();
  list.push(entry);
  list.sort((a, b) => b.equity - a.equity);
  const trimmed = list.slice(0, MAX_SCORES);
  writeScores(trimmed);
  const rank = trimmed.findIndex((s) => s.ts === entry.ts && s.name === entry.name) + 1;
  res.json({ rank: rank || null, total: trimmed.length, top: trimmed.slice(0, 10) });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`阿尔法狂飙 running → http://localhost:${PORT}`);
});
