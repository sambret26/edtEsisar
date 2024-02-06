import sys
sys.path.append("modules")

from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

import cal

load_dotenv()

DBTypes = os.environ.get("DB_TYPE")
if (DBTypes and DBTypes == "REMOTE"):
    import remoteDB as DB
else :
    import localDB as DB


def deleteCal(area):
    calendarData = DB.getCalendarDatas(area)
    creds = cal.findCreds(calendarData[0])
    calendarId = calendarData[1]
    service = build('calendar', 'v3', credentials=creds)
    eventsResult = service.events().list(calendarId=calendarId, singleEvents=True, orderBy='startTime',maxResults=2500).execute()
    events = eventsResult.get('items', [])
    count = 0
    for event in events :
            service.events().delete(calendarId=calendarId, eventId=event['id']).execute()
            count = count + 1
            print(f"Deleted {count}/{len(events)}")
    #print(f"Deleted {count} elements")
    return count

count = 1
while count :
    count = deleteCal("3AS2")
