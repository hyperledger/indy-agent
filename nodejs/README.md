# node.js implementation of the indy-agent

## Quick start guide
* `git clone https://github.com/hyperledger/indy-sdk.git` and follow [the instructions](https://github.com/hyperledger/indy-sdk/tree/master/doc) to build libindy for your system.
* Make sure the indy-sdk node module can access the built library by following [these instructions](https://www.npmjs.com/package/indy-sdk#installing).
* Make sure you have a running ledger by running these commands inside of the indy-sdk repository.

```
docker build -f ci/indy-pool.dockerfile -t indy_pool .
docker run -itd -p 9701-9708:9701-9708 indy_pool
```

* Then run the following commands to start the agent

```
git clone https://github.com/hyperledger/indy-agent.git
cd indy-agent/nodejs
npm install # This will fail if libindy is not accessible
npm start # Starts the node.js express server
```
* Then go to http://localhost:3000

## Agent Configuration
The agent can be configured using the following environment variables, or the values can be edited directly in `config.js`

```
PUBLIC_DID_ENDPOINT=10.0.0.2:3000
TEST_POOL_IP=10.0.0.2
PORT=3000
WALLET_NAME=wallet_3000
FIRST_NAME=Alice
MIDDLE_NAME=Rebecca
LAST_NAME=Garcia
AGE=22
GENDER=F
```

Where PUBLIC_DID_ENDPOINT refers to the host and port your agent is running at, and the TEST_POOL_IP refers to the ip address of the running ledger.
