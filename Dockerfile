FROM python:3.8.3

LABEL maintainer="robin.j.huang@gmail.com"

# We copy just the requirements.txt first to leverage Docker cache
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 wsgi