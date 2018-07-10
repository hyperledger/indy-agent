Indy Agent Test Suite
===================================

This is the Indy Agent Test Suite used to certify standards compliance and interoperability.

The tests run by this test suite are based on approved Hyperledger Indy Project Enhancement (HIPE) proposals.

As the test suite matures, documentation will be added on how to create and add tests to the suite.

Requirements
------------
- Python 3.6
- Latest `libindy` from https://github.com/hyperledger/indy-sdk

Quickstart
----------

First, create a virtual environment to install indy-agent dependencies:

```sh
cd python/
python -m venv env
source env/bin/activate
```

This will create and activate a virtual environment in the `env` directory using the python `venv` module. You may
have to install this module through your system package manager or pip.

Then, to install dependencies, run `pip install .` from the python directory.

Make sure `libindy` is in your `LD_LIBRARY_PATH` and then run:

```sh
python test.py AGENT_IP AGENT_PORT
```

Where `AGENT_IP` is the address of the agent to test and `AGENT_PORT` is the port that the agent is using to listen for
messages.
