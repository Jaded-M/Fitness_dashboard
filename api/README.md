# PHI Mobile API

The FastAPI service is the authenticated backend for the future Flutter client.
Flutter signs in with Supabase Auth and sends the access token as:

```text
Authorization: Bearer <supabase-access-token>
```

Run locally:

```powershell
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_ANON_KEY="your-anon-key"
uvicorn api.main:app --reload
```

The OpenAPI explorer is available at `http://127.0.0.1:8000/docs`.

Core routes:

- `GET /health`
- `GET /api/v1/me`
- `GET|POST /api/v1/workouts`
- `GET /api/v1/workouts/records`
- `GET /api/v1/workouts/{exercise}/last`
- `GET|POST /api/v1/nutrition/logs`
- `GET|PUT /api/v1/activity/steps`
- `GET|POST /api/v1/activity/checkins`
- `GET|POST /api/v1/activity/measurements`
- `GET /api/v1/intelligence/today`
- `GET /api/v1/intelligence/readiness`
- `GET /api/v1/intelligence/body-composition`
