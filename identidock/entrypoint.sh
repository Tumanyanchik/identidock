#!/bin/bash
set -e

# ─── 1. Ждём готовности БД ───────────────────────────────
if [ -n "$DATABASE_URL" ]; then
    echo "[entrypoint] Waiting for database..."
    python - <<'PYEOF'
import os, re, socket, sys, time

url = os.environ["DATABASE_URL"]
m = re.match(r'postgresql://[^:]+:[^@]+@([^:/]+):(\d+)/', url)
if not m:
    print(f"[entrypoint] Cannot parse DATABASE_URL: {url}", file=sys.stderr)
    sys.exit(1)
host, port = m.group(1), int(m.group(2))
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[entrypoint] DB is up at {host}:{port}")
            sys.exit(0)
    except OSError:
        time.sleep(2)
print(f"[entrypoint] DB not reachable at {host}:{port} after 60s", file=sys.stderr)
sys.exit(1)
PYEOF
fi

# ─── 2. Применяем миграции ───────────────────────────────
if [ "$ENV" != "UNIT" ] && [ -n "$DATABASE_URL" ]; then
    if [ -f /app/migrations/alembic.ini ]; then
        echo "[entrypoint] Applying DB migrations..."
        flask db upgrade
    else
        echo "[entrypoint] /app/migrations/alembic.ini not found — skipping migrations."
        echo "[entrypoint] Run 'flask db init' and 'flask db migrate' once to bootstrap."
    fi
fi

# ─── 3. Передаём управление оригинальному cmd.sh ─────────
exec "$@"
