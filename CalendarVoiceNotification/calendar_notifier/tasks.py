from celery import shared_task
from celery.decorators import task
from datetime import datetime
from time import sleep
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS
from django.http import HttpResponse

@shared_task
def sleepy():
	message = 'Five seconds have passed'

	tts = gTTS(message)
	tts.save('test.mp3')

	sound = AudioSegment.from_mp3('test.mp3')
	play(sound)

	return os.getcwd()

@task(name='hello')
def hello(name):
	message = 'Hello {}, the time now is {}'.format(name, datetime.now())
	# return HttpResponse('<h1>' + str(message) + '</h1>')
	return message