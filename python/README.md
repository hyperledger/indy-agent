Indy-agent implementation in Python
===================================

This is an implementation of indy-agent written in Python.

This agent seeks to be as simple as possible while accurately representing the Sovrin protocol.

Requirements
------------
- Python 3.6
- Latest `libindy` from https://github.com/hyperledger/indy-sdk

Quickstart
----------
There are two ways to run the agent (tested on Ubuntu 16.04).  

Change your current folder to `indy-agent/python`  

1. **Using Docker**  
    * Make sure you have Docker installed.
    * Build docker image: `$ docker build -t indy-agent .`
    * Run created container: `$ docker run -p 8094:8094 -e PORT=8094 indy-agent` and keep the terminal window opened
    * Open another instance of terminal and change your current folder to `indy-agent/python`
    * Run another instance of docker container: `$ docker run -p 8095:8095 -e PORT=8095 indy-agent` and keep the terminal window opened
    
    At this moment we have two instances of agents running (on ports 8094 and 8095). In order to interact with them we have to know their assigned ip's.
    * Do `$ sudo iptables -L` and find `Chain DOCKER` table. Info you need is stored at the `destination` column. (in my case I had 172.17.0.2 and 172.17.0.3)
    * Open up your browser, with two tabs opened: 172.17.0.2:8094 (agent A) and 172.17.0.3:8095 (agent B).

2. **Using dev mode**
    
    * Make sure you have Python virtual environment installed and running.
    * Install requirements: `$ pip install -r requirements.txt`
    * In one instance of your terminal: `$ python indy-agent 8094` and don't close it.  
    * In another instance of your terminal: `$ python indy-agent 8095` and don't close it.  
    * Open up your browser, with two tabs opened: localhost:8094 (agent A) and localhost:8095 (agent B).

To this point I hope you have properly launched the agents.  
To do the DEMO (**using both 1 and 2 ways of running the agent**):
* In agent A browser tab type: `Alice` and any password.
* In agent B browser tab type: `Bob` and any password.
* In agent A browser tab click button send connection offer. Type `AliceToBobConnection` and ip-address of the second agent with the /offer route (in my case it was 172.17.0.3:8095/offer), click `send connection offer`
* In agent B browser tab click on the `view` button and check the received message. Click `send request`
* In agent A browser tab click on the `view` button and check the received message. Click `send response`
* In agent B browser tab click on the `view` button and check the received message.