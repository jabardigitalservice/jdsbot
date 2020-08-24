FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD [ "gunicorn", "--bind", "0.0.0.0:80", "server:app" ]
