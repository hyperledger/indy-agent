FROM ubuntu:16.04

ARG uid=1000
ARG indy_stream=stable

ENV LC_ALL="C.UTF-8"
ENV LANG="C.UTF-8"
ENV SHELL="/bin/bash"

# Python 3.6
RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

# Install environment
RUN apt-get update -y && apt-get install -y \
    wget \
    python-setuptools \
    python3-nacl \
    apt-transport-https \
    ca-certificates \
    build-essential \
    pkg-config \
    cmake \
    libssl-dev \
    libsqlite3-dev \
    libsodium-dev \
    curl

# Add indy user
RUN useradd -ms /bin/bash -u $uid indy

# Install LibIndy
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial $indy_stream" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y libindy

WORKDIR /app

COPY . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ARG PORT

ENV PORT=${PORT}

EXPOSE $PORT

CMD python3.6 indy-agent.py $PORT
