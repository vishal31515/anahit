# Running service with virtual environment

## Clone the project
- ` git clone https://github.com/sanjaymeena/anahit_website.git`

## Create python 3.9 virtual environment
  - `python3 -m venv env`
## Activate the environment
  - `source/env/bin/activate`
## Install dependencies mentioned in requirements.txt file
  - `pip install -r requirements.txt`

## Database
  - Postgresql

## Run migrations
  - `python manage.py makemigrations`
  - `python manage.py migrate`

## Create superuser
  - `python manage.py createsuperuser`

## Run service
  - `python manage.py runserver`
  - Go to http://127.0.0.1:8000/

## Cronjob configurations
  - Add cron job to system `python manage.py crontab add`
  - Show current active cron jobs `python manage.py crontab show`
  - Remove all cron jobs `python manage.py crontab remove`

## Hardware Configurations Required
  - Ubuntu 16.0 or > 16.0
  - Minimun 2 GB RAM required.
  - Minimum Python version 3.6 or > 3.6

## Instructions for server deployment

  - Run `sudo service anahit restart && sudo service nginx restart` everytime after new pull request.
  - Run `python manage.py collectstatic` after every new css/js changes.
  - Run `cp -r /home/anahit_web/anahit_website/app/static-temp/* static/` after collectstaic command. So new changes will be copied to staic-temp folder.
  - All static files serving from static-temp directory on server.