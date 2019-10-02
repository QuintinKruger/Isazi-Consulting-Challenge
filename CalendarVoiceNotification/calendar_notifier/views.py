from __future__ import print_function
import sys
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
from .tasks import sleepy, hello
# from datetime import datetime, timedelta

# Create your views here.

def test(request):
    message = hello.delay('Lindie')
    # return HttpResponse('<h1>' + str(message) + '</h1>')

def index(request):
    run_at = datetime.datetime.now() + datetime.timedelta(seconds=10)
    sleepy.apply_async(eta=run_at)
    return render(request, 'calendar_notifier/index.html')

def get_calendar(request):
    # import pdb; pdb.set_trace()
    # return HttpResponse("<h1>This is the quick start function. </h1>")
    # If modifying these scopes, delete the file token.pickle.
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
            print("HEREEEEEEEEEEEEf", flow.authorization_url())
            creds = flow.run_local_server(port=8001)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    events_result = service.events().list(calendarId='primary', singleEvents=True,
                                        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
       return HttpResponse("<p> No upcomming events. </p>")

    todays_events = []
    for event in events:
        participants = []

        # Get the date now to determine if the event will take
        # place today
        now_date = datetime.datetime.now().date()
        
        # Get the date in a python datetime format for
        # comparison
        start_date = dtparse(event['start'].get('dateTime').split('T')[0]).date()

        # datetime_start = 
        if (start_date == now_date):
            print('The event will still happen')
            start_time = dtparse(event['start'].get('dateTime')).time()
            end_time = dtparse(event['end'].get('dateTime', event['end'].get('date'))).time()
            description = event['summary']
            # participants.append(event['attendees'].get())
            # for attendee in event['attendees']:
            #     participants.append(attendee.get('displayName'))

            todays_events.append({'start_time':start_time, 'end_time':end_time, 'description':description})
    for event in todays_events:
        print(event['start_time'])

    # mp3_fp = BytesIO()
    # tts = gTTS('Hello', 'en')
    # tts.write_to_fp(mp3_fp)

    # tts = gTTS(str(event['summary']))
    # tts.save('summary.mp3')

    # sound = AudioSegment.from_mp3('summary.mp3')
    # play(sound)

    context = {'todays_events':todays_events,
               'today': datetime.datetime.now().date()}
    return render(request, 'calendar_notifier/calendar.html', context)
