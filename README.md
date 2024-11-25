This project is using Python 3.12.3 and Django 5.1.2.

To start the development server:
Run this command 'python manage.py runserver'
This will launch the Django development server at http://127.0.0.1:8000/.
You can access your application in your web browser.

To running tests
Run this command 'python manage.py test'
This command will run the unit tests for your application.

To launch this app using docker:
Run this command 'docker-compose up --build'
This will launch the Django development server at http://127.0.0.1:8000/.
You can access your application in your web browser.

To set up and run migrations run this commands:
'python manage.py makemigrations' to make migrations,
'python manage.py migrate' to apply migrations.

To set up translations run this commands:
'django-admin compilemessages'
This command will create .mo files for English to Ukrainian translation.
