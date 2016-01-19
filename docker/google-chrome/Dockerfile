FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y software-properties-common
RUN apt-add-repository multiverse

RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list
RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections

RUN apt-get update && apt-get install -y --force-yes \
    google-chrome-stable \
    msttcorefonts \
    openbox \
    xdotool \
    xvfb

RUN useradd chrome

CMD ["/bin/sleep", "infinity"]
