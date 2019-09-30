from __future__ import print_function
import sys
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
from datetime import datetime, timedelta

# Create your views here.

def index(request):
    sleepy.delay(10)
    # delay = datetime.now() + timedelta(seconds=5)
    return HttpResponse("<h1>Homepage.</h1>")

def quickstart(request):
    # return HttpResponse("<h1>This is the quick start function. </h1>")
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    # """ Shows basic usage of the Google Calendar API.
    # Prints the start and name of the next 10 events on the user's calendar.
    # """
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
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    # mp3_fp = BytesIO()
    # tts = gTTS('Hello', 'en')
    # tts.write_to_fp(mp3_fp)

    tts = gTTS(str(event['summary']))
    tts.save('summary.mp3')

    sound = AudioSegment.from_mp3('summary.mp3')
    play(sound)

    return HttpResponse("<p> " + str(event['summary']) + "</p>")
