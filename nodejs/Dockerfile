# Use BC Gov Indy images that have indy-sdk
# Will have to be updated from time to time to stay up to date on the indy-sdk version
FROM bcgovimages/von-image:py36-1.0rc3

USER root

# Install nodejs
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y \
        nodejs \
        build-essential

WORKDIR $HOME

RUN mkdir nodejs
WORKDIR nodejs

ENV LD_LIBRARY_PATH=$HOME/.local/lib:/usr/local/lib:/usr/lib

# Add package.json to enable using npm install
COPY package.json .
# RUN npm install --save indy-sdk
RUN npm install

# Copy rest of the app
COPY . .

CMD [ "npm", "start" ]