import sys
sys.path.append("modules")

import cal
import DB
from googleapiclient.discovery import build



def deleteCal(area):
    creds = cal.findCreds(area)
    calendarId = DB.getCalendarId(area)
    service = build('calendar', 'v3', credentials=creds)
    eventsResult = service.events().list(calendarId=calendarId, singleEvents=True, orderBy='startTime',maxResults=2500).execute()
    events = eventsResult.get('items', [])
    for event in events :
            service.events().delete(calendarId=calendarId, eventId=event['id']).execute()


deleteCal("3ATP5")
deleteCal("3AS2")
