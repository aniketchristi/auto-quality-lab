#!/bin/sh
set -eu
cd "$(dirname "$0")"
sh scripts/start-db.sh
echo 'Open http://127.0.0.1:8501 in your browser. Press Control-C to stop the dashboard.'
sh scripts/dashboard.sh
