from __future__ import annotations

import os

from supabase import create_client


TABLES = (
    "workouts",
    "food_logs",
    "water_logs",
    "measurements",
    "checkins",
    "steps",
)


def main() -> None:
    url = os.environ.get("SUPABASE_URL", "").strip()
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    owner_id = os.environ.get("PHI_OWNER_USER_ID", "").strip()
    if not url or not service_key or not owner_id:
        raise RuntimeError(
            "SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and PHI_OWNER_USER_ID are required."
        )

    client = create_client(url, service_key)
    for table in TABLES:
        response = (
            client.table(table)
            .update({"user_id": owner_id})
            .is_("user_id", "null")
            .execute()
        )
        print(f"{table}: assigned {len(response.data or [])} legacy row(s)")


if __name__ == "__main__":
    main()
