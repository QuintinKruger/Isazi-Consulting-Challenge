# Isazi-Consulting-Challenge
The calendar voice notification challenge for Isazi Consulting.

# Installation
1. Django
2. Redis
3. Celery

# Usuage
1. Set up a redis server on port 6380 using the command *redis-server --port 6380*.
2. Run celery by executing the command *celery worker -A CalendarVoiceNotification --loglevel=info* in the first _CalendarVoiceNotification_ directory.
3. Run the Django server by navigating to the first _CalendarVoiceNotification_ directory (as before) and exeute the command *python3 manage.py runserver*.
4. Type *http://localhost:8000/calendar_notifier/get_calendar* into a browser.
5. Navigate back to the terminal where the django server was run and follow the link requesting authoriztion to access the user's google calendar (automatic link redirecting cannot work as the development server uses HTTP where as the link uses HTTPS).
6. A table listing upcomming events will be presented as an agenda whose details will be reported 15 minutes prior to the event in question.

# Other Pages
A home page also exists if the user navigates to the *http://localhost:8000/calendar_notifier* url. The homepage provides more details to following the link required for authorization if more clarity is needed.

