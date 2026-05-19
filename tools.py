import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Âmbitos para aceder a Tarefas e Calendário
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/tasks.readonly']

def get_credentials():
    creds = None
    # O ficheiro token.json guarda as credenciais após o primeiro login
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Aqui ele vai procurar o seu credentials.json
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_tasks():
    creds = get_credentials()
    service = build('tasks', 'v1', credentials=creds)
    results = service.tasks().list(tasklist='@default').execute()
    items = results.get('items', [])
    return [task['title'] for task in items] if items else ["Nenhuma tarefa encontrada."]

def get_calendar():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    from datetime import datetime
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return [f"{event['summary']} às {event['start'].get('dateTime', event['start'].get('date'))}" for event in events] if events else ["Agenda livre."]

if __name__ == "__main__":
    print("Buscando tarefas reais...")
    print(get_tasks())
    print("\nBuscando eventos reais...")
    print(get_calendar())