# foodgram-project can be found at http://130.193.43.193/

# About
A dynamic web-site to create, purchase, subscribe to and share food recipes. \
A downloadable text file with amounts of all the ingredients of purchased 
recipes is available on demand.

# Tech stack:

Python 3
Django
PostgreSQL
Docker
Docker-compose
Docker Hub
Gunicorn
Nginx
Github Actions
Ubuntu
HTML, CSS, JavaScript


# Running Instructions
After you've started the server (see the instructions below), 
run the following commands in the system shell:
```buildoutcfg
python manage.py migrate
python manage.py load_fixtures 
python manage.py createsuperuser # to make use of /admin/ endpoint 
```
If "python" doesn't work, try "python3" instead. \
If you have to reload fixtures (ingredient list and tags), you might need to
get rid of the duplicate records. For that run
```buildoutcfg
python manage.py del_dup_ingredients
``` 

## For Development
Set DEBUG = True in recipes/settings.py 
sqlite3 DB is hooked up, the DB file is created in the project folder.
After running in your system shell
```buildoutcfg
python manage.py runserver
```
in your project folder the web server will be available at localhost:8000
Ctrl+C to stop the server.

## For Production
You might want to try and test the project locally before rolling it to production.
In .env file list all the variables accessed in settings.py through os.getenv('VarName'), 
 including DEBUG set to 0.
For Django SECRET_KEY value refer to https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SECRET_KEY
In settings.py set \
DEBUG = bool(int(os.getenv('DEBUG'))) \
Start Docker containers with the application and the PostgreSQL database by running
docker-compose up --build in your system shell. \
N.B. If you are on Windows 10 and testing locally you might want to make
the following changes in your docker-compose.yaml: \
Change
```buildoutcfg
    volumes:
      - postgres_data:/var/lib/postgresql/data/
```
to
```buildoutcfg
    volumes:
      -/c/path/to/db/file/on/c/drive: /var/lib/postgresql/data/
```
Named volumes can fail to run on Windows.
Your app will be available at localhost:80 (or just localhost)

# Deployment
In .env add your host url and IP address to the DJANGO_ALLOWED_HOSTS variable
(use space as the delimiter).
In docker-compose.py change 
```buildoutcfg
    image: timurhamzin/foodgram
```
to
```buildoutcfg
    image: <your_user_name_on_dockerhub>/foodgram
```
 and run docker push. On your remote server through ssh 
 install docker and docker-compose, copy .env, .Dockerfile, 
 docker-compose.yaml and nginx_default.conf to your chosen folder and run
 ```buildoutcfg
docker pull
docker-compose up
docker exec -it <username>_web_1 bash
```
You are now in your web-app docker container. Run the following commands:
```
python manage.py migrate
python manage.py load_fixtures 
python manage.py createsuperuser # to make use of /admin/ endpoint 
```
Your app is available at your host's IP address and url.