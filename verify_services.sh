#!/usr/bin/env bash
# verify_services.sh
# Run `python manage.py check` on every Django microservice.
# Usage:  bash verify_services.sh
#
# Expected result: "System check identified no issues (0 silenced)." for all services.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SERVICES_DIR="$ROOT/services"

# Django services only (realtime-service and ml-service are FastAPI — skip check)
DJANGO_SERVICES=(
    "auth-service"
    "catalog-service"
    "order-service"
    "payment-service"
    "platform-service"
    "reporting-service"
)

PASS=0
FAIL=0
ERRORS=()

for svc in "${DJANGO_SERVICES[@]}"; do
    svc_dir="$SERVICES_DIR/$svc"
    echo ""
    echo "══════════════════════════════════════════"
    echo "  Checking: $svc"
    echo "══════════════════════════════════════════"

    if [ ! -d "$svc_dir" ]; then
        echo "  ⚠️  Directory not found: $svc_dir — skipping"
        continue
    fi

    # Activate virtual env if present, otherwise use system python
    if [ -f "$svc_dir/venv/bin/activate" ]; then
        source "$svc_dir/venv/bin/activate"
    fi

    # Find the Django settings module (assume it matches the service folder name with _ )
    settings_module="$(echo $svc | tr '-' '_').settings"

    cd "$svc_dir"
    if DJANGO_SETTINGS_MODULE="$settings_module" python manage.py check 2>&1; then
        echo "  ✅ $svc — PASS"
        ((PASS++)) || true
    else
        echo "  ❌ $svc — FAIL"
        ((FAIL++)) || true
        ERRORS+=("$svc")
    fi
    cd "$ROOT"
done

# FastAPI services — just import-check main.py
FASTAPI_SERVICES=("realtime-service" "ml-service")
for svc in "${FASTAPI_SERVICES[@]}"; do
    svc_dir="$SERVICES_DIR/$svc"
    echo ""
    echo "══════════════════════════════════════════"
    echo "  Import check: $svc (FastAPI)"
    echo "══════════════════════════════════════════"

    if [ ! -f "$svc_dir/main.py" ]; then
        echo "  ⚠️  main.py not found — skipping"
        continue
    fi

    cd "$svc_dir"
    if python -c "import main" 2>&1; then
        echo "  ✅ $svc — PASS"
        ((PASS++)) || true
    else
        echo "  ❌ $svc — FAIL"
        ((FAIL++)) || true
        ERRORS+=("$svc")
    fi
    cd "$ROOT"
done

echo ""
echo "══════════════════════════════════════════"
echo "  RESULTS: $PASS passed, $FAIL failed"
echo "══════════════════════════════════════════"

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "  Failed services:"
    for e in "${ERRORS[@]}"; do
        echo "    ❌ $e"
    done
    exit 1
else
    echo "  ✅ All services passed."
    exit 0
fi
