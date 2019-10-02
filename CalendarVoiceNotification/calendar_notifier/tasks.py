from celery import shared_task
from celery.decorators import task
from datetime import datetime
from time import sleep
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS
from django.http import HttpResponse
from celery.task import periodic_task
from celery.schedules import crontab

@task(name='make_new_event_announcement')
def make_new_event_announcement(description, start_time, end_time, participants):
	message = '{} in the next 15 minutes - starting at {} and ending at {}. '.format(description, start_time, end_time)
	participants_list = ''

	if len(participants) == 0:
		announcement = message
	else:
		for i in range(len(participants)):
			participants_list = participants_list + str(participants[i]) + ','
		participants_list = participants_list + '.'
		announcement = str(message)+ str('Those that will be attending are ') + str(participants_list)

	tts = gTTS(announcement)
	tts.save('announcement.mp3')

	sound = AudioSegment.from_mp3('announcement.mp3')
	play(sound)

