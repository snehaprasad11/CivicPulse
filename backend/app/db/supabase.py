import os

import httpx


def supabase_configured() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def save_audit_run(payload: dict) -> bool:
    if not supabase_configured():
        return False

    url = f"{os.environ['SUPABASE_URL'].rstrip('/')}/rest/v1/audit_runs"
    headers = {
        "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    response = httpx.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return True
