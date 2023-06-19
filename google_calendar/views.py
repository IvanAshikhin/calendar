from django.shortcuts import render
import datetime
import os.path
from collections import defaultdict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def display_events(request):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.now().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId='4c210a2865e9b8d56514be2a7268c23a21979380f01e020322b1fae528084411@group.calendar.google.com',
            timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime', timeZone='Asia/Almaty').execute()
        events = events_result.get('items', [])

        if not events:
            events = [{'start': '', 'summary': 'No upcoming events found.'}]
        else:
            unique_events = defaultdict(list)
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                unique_events[start[:10]].append(event)

            events = [{'date': date, 'events': unique_events[date]} for date in sorted(unique_events.keys())]

        return render(request, 'events.html', {'events': events})

    except HttpError as error:
        return render(request, 'events.html', {'error': error})
