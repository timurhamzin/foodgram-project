FROM python:3.8.5

LABEL author='timurhamzin' version=1.1.1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV HOME=/foodgram
WORKDIR $HOME

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt && pip install flake8

COPY . .

RUN chmod +x entrypoint.sh

RUN flake8 --ignore=E501,F401,F541,F403,F405 --exclude=venv .

# CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000

ENTRYPOINT ["/foodgram/entrypoint.sh"]
