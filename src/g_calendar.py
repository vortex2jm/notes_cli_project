from __future__ import print_function

import datetime
from multiprocessing import Event
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

# from event import event_body
from entities.event import event_body

#creating class
class Calendar:

    def __init__(self, credentials_file, token_file):
        self.credentials_file = credentials_file
        self.token_file = token_file

    def connect(self):

        #==================creating or refreshing token file=============#
        creds = None
        
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
       
        with open(self.token_file, 'w') as token:
            token.write(creds.to_json())

        #========================creating service==========================#
        try:
            self.calendar = build('calendar', 'v3', credentials=creds)

        except HttpError as error:
            print(error)


    def __edit_event(self, name, start_date, end_date, start_time, end_time, description, location):
        event_body['summary'] = name
        event_body['location'] = location
        event_body['description'] = description
        event_body['start']['dateTime'] = f'{start_date}T{start_time}:00-03:00'
        event_body['end']['dateTime'] = f'{end_date}T{end_time}:00-03:00'


    def create_event(self, name, start_date, end_date, start_time, end_time, description, location):

        #Function to edit request body
        self.__edit_event(name, start_date, end_date, start_time, end_time, description, location)

        event = self.calendar.events().insert(calendarId='primary', body=event_body).execute()
        print ('\nEvent created: %s\n\n' % (event.get('htmlLink')))


    def list_events(self):
        
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Listing the upcoming 10 events')
        events_result = self.calendar.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        print('====Events====\n')

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for index,event in enumerate(events):

            start = event['start']['dateTime']
            start = start.split('T')

            date = start[0]

            hour = start[1].split('-')
            hour = hour[0]
            hour = hour[0:5]

            print(f'{index + 1} -> ', event['summary'], f'|| {date} at {hour}h')

        return events
    
    def delete_event(self, event_id):
        self.calendar.events().delete(calendarId='primary', eventId=event_id).execute()
        print('event deleted!')