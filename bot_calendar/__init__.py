from __future__ import print_function

import configparser
import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build

config = configparser.ConfigParser()
config.read('config.ini')

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

CALENDAR_ID = config['Calendar']['calendar_id']
BOT_SERVICE_ID = config['Calendar']['bot_sevice_id']
SERVICE_ACCOUNT_FILE = config['Calendar']['service_credentials']
SLOT_SIZE_MIN = int(config['Workday']['slot_size_min'])


def set_event(order):
    # setting service
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    message_text = order.name + " " + order.phone
    # dat=order.date.strftime("%Y-%M-%D")
    start = datetime.datetime(order.date.year, order.date.month, order.date.day, int(order.hours), int(order.minutes),
                              00, 000000)
    end = start + datetime.timedelta(minutes=SLOT_SIZE_MIN)
    # dat =dat +"T"+order.hours+":"+order.minutes+":00+03:00"

    event = {
        'summary': message_text,

        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'Asia/Jerusalem'
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'Asia/Jerusalem'
        },

    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()


def update_schedule_for_date(schedule, date):
    events = get_events_for_date(date)

    for event in events:
        startF = event['start']['dateTime']
        startT = startF.split('T')[1]
        startH = int(startT.split(':')[0])
        startM = int(startT.split(':')[1])
        sum = event['summary']
        schedule[startH][startM] = sum

    return schedule


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def get_events_for_date(date):
    try:

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('calendar', 'v3', credentials=creds)

        dt = datetime.datetime.combine(date, datetime.datetime.min.time())

        now = dt.isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events
    except Exception as e:
        print(e)


if __name__ == '__main__':
    now = datetime.datetime.now()
    main()
