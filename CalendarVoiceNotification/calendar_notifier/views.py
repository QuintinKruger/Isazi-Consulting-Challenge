from __future__ import print_function
import sys
from django.shortcuts import redirect
from django.shortcuts import render
from dateutil.parser import parse as dtparse
from gtts import gTTS
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pydub import AudioSegment
from pydub.playback import play
from .tasks import make_new_event_announcement
from time import sleep


# Create your views here.
def index(request):
    run_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
    return render(request, 'calendar_notifier/index.html')



def get_calendar(request):
    # what permission the application has with the user's calendar
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    # filter only those events that will still take place in the
    # future
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    # No new events for today, nnounce this but
    # carry on with script to return html page that will
    # display a similar message
    if (len(events) == 0):
        message = 'You have no new events for today. An update will be made tomorrow to checkyour schedule then.'
        tts = gTTS(message)
        tts.save('test.mp3')

        sound = AudioSegment.from_mp3('test.mp3')
        play(sound)

    todays_events = []
    for event in events:
        particpants = []
        # start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = dtparse(event['start'].get('dateTime')).time()
        end_time = dtparse(event['end'].get('dateTime', event['end'].get('date'))).time()
        description = event['summary']
        
        # Add to the events that need to be announced
        todays_events.append({'start_time':start_time, 'end_time':end_time, 'description':description})
       
        # The event might not have attendees listed, test for this
        attendees = event.get('attendees')
        if attendees is not None:
            for participant in attendees:
                # A user might not have a displayName field, test for this
                displayName = participant.get('displayName')
                if displayName is not None:
                    particpants.append(displayName)



        # Schedule the event to be announced 15 minutes before the start time
        start = dtparse(event['start'].get('dateTime', event['end'].get('date')))
        run_at = start - datetime.timedelta(minutes=15)
        make_new_event_announcement.apply_async((description, start_time, end_time, particpants), eta=run_at)

    context = {'todays_events':todays_events,
               'today': datetime.datetime.now().date()}
    return render(request, 'calendar_notifier/calendar.html', context)
