# 年度见人计划 · People Planner

一个零依赖的单页应用，用来规划"今年想见的人"和记录"已经见过的人"。

## 用法

直接在浏览器打开 `index.html` 即可，无需安装。

### 在手机上使用

有两种方式：

**A. 立即预览（无需任何配置）**
在手机浏览器打开（推荐 Safari / Chrome）：

```
https://raw.githack.com/linxusong0819-eng/claude-code-T01/claude/people-meeting-planner-ENRak/index.html
```

合并到 `main` 后稳定地址：

```
https://raw.githack.com/linxusong0819-eng/claude-code-T01/main/index.html
```

**B. 用 GitHub Pages 部署（推荐，URL 更短）**
1. 仓库 → Settings → Pages
2. Source 选 **GitHub Actions**
3. 把这个 PR 合到 `main`，工作流会自动发布到：
   `https://linxusong0819-eng.github.io/claude-code-T01/`

### 添加到手机主屏幕（像 App 一样用）
- **iPhone (Safari)**：打开页面 → 分享 → "添加到主屏幕"
- **Android (Chrome)**：打开页面 → 右上角菜单 → "添加到主屏幕"

数据保存在该域名下的浏览器存储中，关掉浏览器也不会丢。

- **新增**：填写姓名、日期、地点、主题、备注；状态默认按日期自动判断（过去=已见，未来=待见），也可手动指定。
- **时间轴**：按月份分组，自动统计每月人数与已见数。
- **筛选**：全部 / 待见 / 已见 / 本月，叠加关键字搜索（姓名、主题、备注、地点）。
- **快捷操作**：✓ 标记为已见，↺ 改回待见，✎ 编辑，✕ 删除。
- **导出 / 导入**：JSON 文件，方便备份或多设备迁移。

## 数据存储

所有数据保存在浏览器的 `localStorage`，**不会上传到任何服务器**。建议定期使用「导出」按钮做备份。

> 注意：数据按"域名 + 浏览器"隔离。手机和电脑各自独立，需要同步时用「导出 / 导入」JSON。
