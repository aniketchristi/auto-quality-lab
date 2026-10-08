#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
PG_BIN="${AUTO_QUALITY_PG_BIN:-/opt/homebrew/opt/postgresql@18/bin}"
mkdir -p .runtime/socket
if [ ! -f .runtime/postgres/PG_VERSION ]; then
  "$PG_BIN/initdb" -D "$PWD/.runtime/postgres" --auth-local=trust --auth-host=trust --encoding=UTF8 --no-locale
  cat >> .runtime/postgres/postgresql.conf <<EOF
listen_addresses = '127.0.0.1'
port = 55432
unix_socket_directories = '$PWD/.runtime/socket'
EOF
fi
if ! "$PG_BIN/pg_ctl" -D "$PWD/.runtime/postgres" status >/dev/null 2>&1; then
  "$PG_BIN/pg_ctl" -D "$PWD/.runtime/postgres" -l "$PWD/.runtime/postgres.log" start
fi
if ! "$PG_BIN/psql" -h 127.0.0.1 -p 55432 -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='auto_quality'" | rg -q 1; then
  "$PG_BIN/createdb" -h 127.0.0.1 -p 55432 auto_quality
fi
echo 'Project PostgreSQL is ready on 127.0.0.1:55432.'
