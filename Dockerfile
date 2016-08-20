FROM ubuntu:16.04

RUN apt-get update && \
    apt-get -y install python \
                       python-dev \
                       python-pip \
                       python-virtualenv \
                       \
                       libpq-dev \
                       \
                       wget

RUN python -m virtualenv --python=python /virtualenv

RUN /virtualenv/bin/pip install uwsgi

RUN mkdir /themyarchive
RUN mkdir /themyarchive/themyarchive
RUN touch /themyarchive/themyarchive/__init__.py
ADD setup.py /themyarchive/setup.py

WORKDIR /themyarchive
RUN /virtualenv/bin/pip install Flask==0.11.1
RUN /virtualenv/bin/python setup.py develop

RUN rm -rf /themyarchive/themyarchive
ADD alembic.ini /themyarchive/alembic.ini
ADD alembic /themyarchive/alembic
ADD docker /themyarchive/docker
ADD themyarchive /themyarchive/themyarchive
