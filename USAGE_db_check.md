# 数据库写入权限检测脚本

`check_db_write_permission.py` 用来判断某个 MySQL / 阿里云 RDS 库当前是否**还开放写入权限**。
检测是**非破坏性**的：真正的写入放在事务里执行并立即回滚，不留任何数据。

## 为什么需要在本地/白名单机器上跑

阿里云 RDS 默认有 **IP 白名单**，且 MySQL 走 3306（原始 TCP）端口。
云端沙箱等只允许 443/HTTPS 出站的环境无法直连，必须在一台
**公网 IP 已加入该实例白名单** 的机器上运行本脚本。

## 依赖

```bash
pip install pymysql cryptography
```

## 用法

凭据可通过命令行参数、环境变量或交互式输入密码提供（脚本内不硬编码任何密码）。

```bash
python3 check_db_write_permission.py \
    --host rm-xxxx.mysql.cn-shenzhen.rds.aliyuncs.com \
    --port 3306 \
    --user <账号> \
    --database <库名>
# 运行后会提示输入密码；也可用 --password 或环境变量 DB_PASSWORD 传入
```

环境变量方式：`DB_HOST` `DB_PORT` `DB_USER` `DB_PASSWORD` `DB_NAME`

## 输出说明

脚本依次输出：

1. **GRANTS** —— 当前账号的授权，看是否包含 `INSERT/UPDATE/DELETE/...` 或 `ALL PRIVILEGES`
2. **read_only 标志** —— 实例是否被设为只读（欠费、锁定或手动设置时为 `1`）
3. **LIVE WRITE PROBE** —— 真实写入探测（事务内回滚）
4. **VERDICT** —— 最终判断：
   - `WRITE ACCESS: OPEN` 写入开放
   - `WRITE ACCESS: CLOSED` 写入已关闭（无写权限，或实例只读）
   - `WRITE ACCESS: UNCERTAIN` 有写授权但探测失败（需看具体报错）
