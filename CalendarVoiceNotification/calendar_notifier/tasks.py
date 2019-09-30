from celery import shared_task
from celery.decorators import task
from datetime import datetime
from time import sleep
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS

@shared_task
def sleepy(duration):
	message = 'Hello it is me, im giving up on you'

	sleep(duration)
	tts = gTTS(message)
	tts.save('test.mp3')

	import os
	print(os.getcwd())
	sound = AudioSegment.from_mp3('test.mp3')
	play(sound)

	return os.getcwd()

@task(bind=True)
def hello():
	print('Hello, the time now is {}'.format(datetime.now()))