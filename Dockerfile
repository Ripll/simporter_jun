# pull official base image
FROM python:3.8-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
# set work directory
WORKDIR /app

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
COPY ./test_data.csv /app/test_data.csv

RUN pip install -r /app/requirements.txt

# copy project
COPY . ./