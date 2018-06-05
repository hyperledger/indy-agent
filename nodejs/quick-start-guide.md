# Quick start Instructions

If you you want to run this code locally, you can follow the [with docker](running-locally-with-docker) or [without docker](running-locally-without-docker) instructions.

If you are planning to contribute to the development of this agent implementation, fork the Indy Agent repo ([git clone https:/github.com/hyperledger/indy-agent.git](git clone https:/github.com/hyperledger/indy-agent.git)) and then in the instructions below, clone your forked version of the repo vs. the hyperledger version. Then use pull requests to submit your code contributions.

These instructions assume you have git installed, docker if you are going to use it, and you are familiar with using a shell/terminal. On Windows, as long as you are using the git-bash shell or the Windows Subsystem for Linux as your shell, you should be fine.

# Running locally WITH Docker

* `git clone https://github.com/bcgov/von-network.git` and in a bash shell (terminal) follow the ["run locally" instructions](https://github.com/bcgov/von-network#running-the-network-locally) to stand up a standard 4-node Hyperledger Indy network.
    * Check that the network is running by accessing [http://localhost:9000](http://localhost:9000)
* Clone this repo (`git clone https:/github.com/hyperledger/indy-agent.git`) and then in a second bash shell, get to the root of the cloned repo, and:
    * `cd nodejs  # change into this directory`
    * `./manage build   # Build the agent docker container`
    * Verifiy the Indy network is running (previous step)
    * `./manage start   # Run the agents`
* Once you have started the agents, you can access the agents at:
    * Agent1: [http://localhost:3000](http://localhost:3000)
    * Agent2: [http://localhost:3001](http://localhost:3001)

The next time you have to start the network and agents run the `./manage start` command in each cloned repo - von-network first, then indy-agent/nodejs.

If you change the nodejs code, you must run the `./manage build` command, but it will be pretty quick as the only step to be repeated is the copying of the nodejs code into the container.  If the `package.json` file changes, the build will take longer to run as the `npm install` step must be run.

Both versions of the `./manage` script have other sub-commands - run `./manage` (no arguments) to see the list.  The "rm" commands are useful for restarting from scratch, including for von-network, deleting the Indy Network ledger (e.g. reverting to just having a Steward on the ledger), and for the nodejs agents to delete their wallets. If you delete the Indy Network ledger, you *MUST* delete the nodejs agent wallets. 

# Running locally WITHOUT Docker

Here are the quick start instructions to running an agent instance locally without docker:

* `git clone https://github.com/hyperledger/indy-sdk.git` and follow [the instructions](https://github.com/hyperledger/indy-sdk/tree/master/doc) to build libindy for your system.
* Make sure the indy-sdk node module can access the built library by following [these instructions](https://www.npmjs.com/package/indy-sdk#installing).
* Make sure you have a running ledger by running these commands inside of the indy-sdk repository.

```
docker build -f ci/indy-pool.dockerfile -t indy_pool .
docker run -itd -p 9701-9708:9701-9708 indy_pool
```

* Then run the following commands to start the agent

```
git clone https:/github.com/hyperledger/indy-agent.git
cd indy-agent/nodejs
npm install # This will fail if libindy is not accessible
# Set environment variables as appropriate:
RUST_LOG=trace
PUBLIC_DID_ENDPOINT=127.0.0.1:3000
WALLET_NAME=wallet_3000
TEST_POOL_IP=127.0.0.1
PORT=3000
npm start # Starts the node.js express server
```
* Then go to [http://localhost:3000](http://localhost:3000)

## Starting a second instance:

To start a second agent instance, change the "3000"s in the environment variables above to be "3001" (or any other port) and then access the agent on that localhost port (e.g. [http://localhost:3001](http://localhost:3001))
