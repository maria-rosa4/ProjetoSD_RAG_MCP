import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/tasks.readonly",
    "https://www.googleapis.com/auth/tasks",
]


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds.has_scopes(SCOPES):
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_tasks():
    creds = get_credentials()
    service = build("tasks", "v1", credentials=creds)
    results = service.tasks().list(tasklist="@default").execute()
    items = results.get("items", [])
    return [task["title"] for task in items] if items else ["Nenhuma tarefa encontrada."]


def create_task(title, notes=None):
    creds = get_credentials()
    service = build("tasks", "v1", credentials=creds)
    body = {"title": title}
    if notes:
        body["notes"] = notes
    task = service.tasks().insert(tasklist="@default", body=body).execute()
    return {"id": task.get("id"), "title": task.get("title")}


def delete_task(task_id):
    creds = get_credentials()
    service = build("tasks", "v1", credentials=creds)
    service.tasks().delete(tasklist="@default", task=task_id).execute()
    return {"deleted": True, "task_id": task_id}


def get_calendar():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    from datetime import datetime

    now = datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return [
        f"{event['summary']} as {event['start'].get('dateTime', event['start'].get('date'))}"
        for event in events
    ] if events else ["Agenda livre."]


def create_calendar_event(summary, start_datetime, end_datetime, description=None):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    body = {
        "summary": summary,
        "start": {"dateTime": start_datetime},
        "end": {"dateTime": end_datetime},
    }
    if description:
        body["description"] = description
    event = service.events().insert(calendarId="primary", body=body).execute()
    return {"id": event.get("id"), "summary": event.get("summary")}


def delete_calendar_event(event_id):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return {"deleted": True, "event_id": event_id}


if __name__ == "__main__":
    print("Buscando tarefas reais...")
    print(get_tasks())
    print("\nBuscando eventos reais...")
    print(get_calendar())
