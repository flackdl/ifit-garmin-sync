FROM python:3.8-buster
ADD src /app
ADD requirements.txt /app
ADD entrypoint.sh /app
WORKDIR /app
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --no-input
ENTRYPOINT /app/entrypoint.sh
