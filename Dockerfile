FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8

# copy only requirements.txt as it rarely changed. This is done to utilize
# docker layer caching, thus avoid calling 'pip install' during every build
# ref: https://towardsdatascience.com/docker-for-python-development-83ae714468ac#3837
COPY requirements.txt /app/
WORKDIR /app

# setup timezone according to https://gitlab.alpinelinux.org/alpine/aports/-/issues/5543#note_109075
RUN apk upgrade --update \
  && apk add -U tzdata \
  && cp /usr/share/zoneinfo/Asia/Jakarta /etc/localtime \
  && apk del tzdata \
  && pip3 install -r requirements.txt

# copy full working dirs
COPY . /app

EXPOSE 80

CMD gunicorn --bind 0.0.0.0:80 example:app -k uvicorn.workers.UvicornWorker
