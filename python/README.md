indy-agent implementation in Python
===================================

This is an implementation of indy-agent written in Python.

This agent seeks to be as simple as possible while accurately representing the Sovrin protocol.

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
python indy-agent.py
```
