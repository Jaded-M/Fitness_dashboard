from __future__ import annotations

import os
import pickle
from datetime import datetime, timedelta

import database

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    GOOGLE_FIT_AVAILABLE = True
except ImportError:
    GOOGLE_FIT_AVAILABLE = False


SCOPES = ["https://www.googleapis.com/auth/fitness.activity.read"]


def get_google_fit_service():
    """Create an authenticated Google Fit service if credentials are available."""
    if not GOOGLE_FIT_AVAILABLE:
        return None, "Google Fit dependencies are not installed."

    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token_file:
            creds = pickle.load(token_file)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("fitness_credentials.json"):
                return None, "Missing fitness_credentials.json."
            flow = InstalledAppFlow.from_client_secrets_file("fitness_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token_file:
            pickle.dump(creds, token_file)

    return build("fitness", "v1", credentials=creds), None


def sync_google_fit_data(start_date, end_date):
    """
    Sync Google Fit daily steps into the local SQLite database.
    Returns (success, message).
    """
    service, error = get_google_fit_service()
    if not service:
        return False, error

    current_start = start_date
    while current_start <= end_date:
        current_end = min(current_start + timedelta(days=14), end_date)

        body = {
            "aggregateBy": [
                {
                    "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
                }
            ],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": int(datetime.combine(current_start, datetime.min.time()).timestamp() * 1000),
            "endTimeMillis": int(datetime.combine(current_end, datetime.max.time()).timestamp() * 1000),
        }

        try:
            response = service.users().dataset().aggregate(userId="me", body=body).execute()
        except Exception as exc:
            return False, f"Sync failed for {current_start} to {current_end}: {exc}"

        for bucket in response.get("bucket", []):
            date_str = datetime.fromtimestamp(int(bucket["startTimeMillis"]) / 1000).strftime("%Y-%m-%d")
            steps = 0
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for value in point.get("value", []):
                        steps += value.get("intVal", 0)

            distance = round(steps * 0.00076, 2)
            active_minutes = round(steps / 100, 0)
            database.add_steps(date_str, steps, distance, active_minutes)

        current_start = current_end + timedelta(days=1)

    database.get_steps_data.clear()
    return True, f"Synced Google Fit activity from {start_date} to {end_date}."
