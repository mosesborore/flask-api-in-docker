FROM python:3.7.5-slim

WORKDIR /api
# set up and activate virtual environment
# ENV VIRTUAL_ENV '/venv'
# RUN python -m venv $VIRTUAL_ENV
# ENV PATH "$VIRTUAL_ENV/bin:$PATH"

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /api

RUN pip install -r requirements.txt

CMD python api.py
