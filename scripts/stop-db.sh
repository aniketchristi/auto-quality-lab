#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
"${AUTO_QUALITY_PG_BIN:-/opt/homebrew/opt/postgresql@18/bin}/pg_ctl" -D "$PWD/.runtime/postgres" stop -m fast
