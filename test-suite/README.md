Indy Agent Test Suite
=====================

This is the Indy Agent Test Suite used to certify standards compliance and interoperability.

The tests run by this test suite are based on approved Hyperledger Indy Project Enhancement (HIPE) proposals.

As the test suite matures, documentation will be added on how to create and add tests to the suite.

Requirements
------------
- Python 3.6
- `libindy` version 1.6.1 from https://github.com/hyperledger/indy-sdk

Quickstart
----------

The test-suite contains two executable python scripts. One is the test suite itself, or the "testing agent," and the
other is a testable but limited agent that can be used as the "tested agent."

Complete the steps described here, and you will be able to run the test suite against the limited agent.

### Step 1: Install dependencies
Create a python virtual environment for installing dependencies. From the `test-suite` directory:

```sh
python -m venv env
source env/bin/activate
```

This will create and activate a virtual environment in the `env` directory using the python `venv` module. You may
have to install this module through your system package manager or pip.

Then install dependencies by running:

```sh
pip install .
```

Ensure `libindy` is in your `LD_LIBRARY_PATH` (if you built from source).

### Step 2: Start the tested agent

At this point, starting the tested agent is as simple as

```sh
python agent.py
```

By default, this will start the agent listening on port 3001.

You can further configure the agent by editing `agent_config.py`.

### Step 3: Start the test suite

```sh
python test.py
```

This will execute the tests contained in the folders listed in the `tests` configuration option.

```toml
# A list of tests to be run by the test agent.
tests = [
    "hello_world",
    "core"
]
```

The above `tests` configuration will execute tests contained in the `tests/hello_world` and the `tests/core`
directories.
