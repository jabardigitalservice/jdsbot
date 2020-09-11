FROM python:alpine3.7

COPY . /app
WORKDIR /app

# setup timezone according to https://gitlab.alpinelinux.org/alpine/aports/-/issues/5543#note_109075
RUN apk upgrade --update \
  && apk add -U tzdata \
  && cp /usr/share/zoneinfo/Asia/Jakarta /etc/localtime \
  && apk del tzdata \
  && pip3 install -r requirements.txt

EXPOSE 80

CMD [ "gunicorn", "--bind", "0.0.0.0:80", "server:app" ]
