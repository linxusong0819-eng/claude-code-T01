#!/usr/bin/env python3
"""Check whether a MySQL/RDS database still grants write access.

The check is non-destructive:
  1. Reads the current user's grants (SHOW GRANTS).
  2. Reads the instance read_only / super_read_only flags.
  3. Runs a real write inside a transaction that is always ROLLED BACK,
     so no data is left behind.

Credentials are taken from CLI flags, then environment variables, then an
interactive prompt for the password. Nothing is hardcoded.

Env vars: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

Example:
  python3 check_db_write_permission.py \
      --host rm-xxxx.mysql.cn-shenzhen.rds.aliyuncs.com \
      --port 3306 --user hk0312 --database hk0312
"""
import argparse
import getpass
import os
import sys

try:
    import pymysql
except ImportError:
    sys.exit("Missing dependency. Install it with:  pip install pymysql cryptography")


def parse_args():
    p = argparse.ArgumentParser(description="Check MySQL write permission (non-destructive).")
    p.add_argument("--host", default=os.getenv("DB_HOST"))
    p.add_argument("--port", type=int, default=int(os.getenv("DB_PORT", "3306")))
    p.add_argument("--user", default=os.getenv("DB_USER"))
    p.add_argument("--password", default=os.getenv("DB_PASSWORD"))
    p.add_argument("--database", default=os.getenv("DB_NAME"))
    p.add_argument("--timeout", type=int, default=15)
    a = p.parse_args()
    missing = [n for n in ("host", "user", "database") if not getattr(a, n)]
    if missing:
        p.error("missing required value(s): " + ", ".join(missing)
                + " (pass as flags or via DB_HOST/DB_USER/DB_NAME env vars)")
    if a.password is None:
        a.password = getpass.getpass("DB password: ")
    return a


def main():
    a = parse_args()
    try:
        conn = pymysql.connect(host=a.host, port=a.port, user=a.user,
                               password=a.password, database=a.database,
                               connect_timeout=a.timeout, read_timeout=a.timeout)
    except Exception as e:
        sys.exit(f"Could not connect: {type(e).__name__}: {e}")

    cur = conn.cursor()

    cur.execute("SELECT VERSION(), CURRENT_USER(), USER()")
    version, current_user, user = cur.fetchone()
    print(f"Connected. Server {version}, authenticated as {current_user} (login {user})\n")

    cur.execute("SHOW GRANTS FOR CURRENT_USER()")
    grants = [r[0] for r in cur.fetchall()]
    print("=== GRANTS ===")
    for g in grants:
        print("  " + g)

    grant_text = " ".join(grants).upper()
    write_privs = ["INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]
    has_all = "ALL PRIVILEGES" in grant_text
    granted_writes = [p for p in write_privs if has_all or f" {p}" in f" {grant_text}"]

    # read_only flags (may require privileges; ignore failures)
    ro_global = ro_super = None
    try:
        cur.execute("SELECT @@global.read_only, @@global.super_read_only")
        ro_global, ro_super = cur.fetchone()
    except Exception as e:
        print(f"\n(could not read read_only flags: {e})")
    if ro_global is not None:
        print(f"\nInstance read_only={ro_global}, super_read_only={ro_super}")

    # Live, rolled-back write probe.
    print("\n=== LIVE WRITE PROBE (rolled back) ===")
    live_write_ok = False
    write_err = None
    try:
        conn.begin()
        cur.execute("CREATE TEMPORARY TABLE _perm_check_tmp (id INT)")
        cur.execute("INSERT INTO _perm_check_tmp VALUES (1)")
        conn.rollback()
        live_write_ok = True
        print("  Write succeeded (then rolled back).")
    except Exception as e:
        write_err = f"{type(e).__name__}: {e}"
        print(f"  Write blocked -> {write_err}")
        try:
            conn.rollback()
        except Exception:
            pass

    cur.close()
    conn.close()

    print("\n=== VERDICT ===")
    if live_write_ok:
        print("WRITE ACCESS: OPEN  (writes accepted; grants: "
              + (", ".join(granted_writes) if granted_writes else "ALL") + ")")
    else:
        if ro_global:
            print("WRITE ACCESS: CLOSED  (instance is in read_only mode)")
        elif granted_writes:
            print("WRITE ACCESS: UNCERTAIN  (grants include "
                  + ", ".join(granted_writes) + " but the probe failed: "
                  + str(write_err) + ")")
        else:
            print("WRITE ACCESS: CLOSED  (no write privileges granted; probe failed: "
                  + str(write_err) + ")")


if __name__ == "__main__":
    main()
