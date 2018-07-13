FROM ubuntu:16.04

USER root

# Install environment
RUN apt-get update -y && \
apt-get install -y \
    git \
    curl \
    build-essential \
    pkg-config \
    cmake \
    libssl-dev \
    libsqlite3-dev \
    libzmq3-dev \
    libncursesw5-dev \
    apt-transport-https \
    ca-certificates

# libindy requires the modern 1.0.14 version of libsodium but Ubuntu 16.04 does not support installation it's from apt repository. 
# Because of this, it requires to build and install libsodium from source:
RUN cd /tmp && \
  curl https://download.libsodium.org/libsodium/releases/libsodium-1.0.14.tar.gz | tar -xz && \
   cd /tmp/libsodium-1.0.14 && \
   ./configure --disable-shared && \
   make && \
   make install && \
   rm -rf /tmp/libsodium-1.0.14

ENV HOME=/app
WORKDIR $HOME

# Install rust toolchain
RUN curl -o rustup https://sh.rustup.rs
RUN chmod +x rustup
RUN ./rustup -y

# Build libindy
RUN git clone https://github.com/hyperledger/indy-sdk.git
WORKDIR $HOME/indy-sdk/libindy
#RUN git fetch
#RUN git checkout db5a92655ea4edd06795d9ed19284aece3815a21
RUN $HOME/.cargo/bin/cargo build

# Move libindy to lib path
RUN mv target/debug/libindy.so /usr/lib

ENV LD_LIBRARY_PATH=$HOME/.local/lib:/usr/local/lib:/usr/lib

# Remove build tool chain
RUN rm -rf $HOME/.cargo \
#  $HOME/indy-sdk \
  $HOME/.rustup \
  $HOME/.multirust \
  $HOME/rustup

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 68DB5E88
ARG indy_stream=stable
RUN echo "deb https://repo.sovrin.org/deb xenial $indy_stream" >> /etc/apt/sources.list

WORKDIR $HOME

# Install nodejs
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update -y && apt-get install -y \
        nodejs \
        build-essential

# Build indy-sdk nodejs wrapper
WORKDIR indy-sdk/wrappers/nodejs
RUN npm install

WORKDIR $HOME
RUN mkdir -p indy-agent/nodejs
WORKDIR indy-agent/nodejs

# Add package.json to enable using npm install
COPY package.json .
# use the newest indy-sdk package
RUN npm install --save $HOME/indy-sdk/wrappers/nodejs
RUN npm install

# Copy rest of the app
COPY . .

CMD [ "npm", "start" ]