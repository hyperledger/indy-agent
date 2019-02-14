Indy Agent Test Suite
=====================

This is the Indy Agent Test Suite used to certify standards compliance and interoperability.

The tests run by this test suite are based on approved Hyperledger Indy Project Enhancement (HIPE) proposals.

As the test suite matures, documentation will be added on how to create and add tests to the suite.

Requirements
------------
- Python 3.6
- `libindy` version 1.8.0 from https://github.com/hyperledger/indy-sdk

Quickstart
----------

### Step 1: Install dependencies
Create a python virtual environment for installing dependencies. From the `test-suite` directory:

```sh
python -m venv env
source env/bin/activate
```

You may have to specify `python3` depending on the default python version for your system.

This will create and activate a virtual environment in the `env` directory using the python `venv` module. You may
have to install this module through your system package manager or pip.

Then install dependencies by running:

```sh
pip install -r requirements.txt
```

Ensure `libindy` is in your `LD_LIBRARY_PATH` (if you built from source).

### Step 2: Configure the test suite

Configuration options are listed in `config.toml`. Descriptions of each option are given there.

The defaults are as follows:

Option | Value
-------|-------
Testing Agent (test-suite) Host and Port | `localhost:3000`
Testing Agent Message URL | `http://localhost:3000/indy`
Tested Agent Message URL | `http://localhost:3001/indy`
Transport Protocol | HTTP
Testing agent wallet | `testing-agent`
Wallet Path | `.testing-wallets`
Clear wallets (delete wallet after testing complete) | `true`
Log level | Warning (`30`)
Tests | `connection.manual`

> **Note:** Some of these defaults don't make as much sense when considering other transport methods like bluetooth or
> NFC or others. When the need (and implementation) arises for these other transport options, the structure of these
> settings will likely change.

You will need to alter the above settings to match your needs.

### Step 3: Start the tested agent

Follow the instructions for starting the agent you are attempting to test.

### Step 4: Run the test suite

```sh
pytest
```

This will execute the tests selected in `config.toml`.

Writing Tests
-------------

Tests follow standard `pytest` conventions. However, due to the asynchronous nature of most Indy-SDK calls and agent
messaging, most tests will likely need `await` a promise and must be marked as asynchronous, e.g.:

```python
@pytest.mark.asyncio
async def test_method():
	await some_indy_sdk_call()
```

Several tools are made available through the test suite to simplify some common tasks.

------------------------------------------------------------------------------------------------------------------------

### Fixtures

Several `pytest` fixtures are defined in `conftest.py`. You may view that file for details on each of these fixtures. A
summary of each will be given here.

#### Usage

Pytest will automatically inject fixtures into test functions when given as parameters matching the fixture names:

```python
async def test_method(config, wallet_handle, transport):
	await some_indy_sdk_call(wallet_handle)
```

The above `test_method` will receive the fixture matching the names `config`, `wallet_handle`, and `transport`.

------------------------------------------------------------------------------------------------------------------------

#### Event Loop

Property| Value
--------|-------------
Fixture | `event_loop`
Scope   | Session
Depends on | None
Dependent Fixtures | `transport`

**Description:** The `event_loop` fixture provides an asynchronous event loop for Python `asyncio` tasks. It is unlikely
that you will need to use this fixture directly in your testing and is mostly used in starting transports.

------------------------------------------------------------------------------------------------------------------------

#### Config

Property| Value
--------|-------------
Fixture | `config`
Scope   | Session
Depends on | None
Dependent Fixtures | `logger`, `wallet_handle`, `transport`

**Description:** The `config` fixture is an object representation of the configuration options in `config.toml`

------------------------------------------------------------------------------------------------------------------------

#### Logger

Property| Value
--------|-------------
Fixture | `logger`
Scope   | Session
Depends on | `config`
Dependent Fixtures | `wallet_handle`, `transport`

**Description:** The `logger` fixture is a python `logging.Logger` to be used for logging during tests. Pytest prints
logs from failing tests after completion.

------------------------------------------------------------------------------------------------------------------------

#### Wallet Handle

Property| Value
--------|-------------
Fixture | `wallet_handle`
Scope   | Session
Depends on | `config`, `logger`
Dependent Fixtures | None

**Description:** The `wallet_handle` fixture provides a session persistent handle to the Indy-SDK wallet. This fixture
automatically closes and deletes (if the `clear_wallets` is configuration option is `true`) the wallet on test session
termination.

------------------------------------------------------------------------------------------------------------------------

#### Transport

Property| Value
--------|-------------
Fixture | `transport`
Scope   | Session
Depends on | `config`, `event_loop`, `logger`
Dependent Fixtures | None

**Description:** The `transport` fixture provides a transport mechanism based on the `transport` configuration option.
At present, only HTTP transport is implemented.

------------------------------------------------------------------------------------------------------------------------

### Helper Functions

Several helper functions are defined in `tests/__init__.py` and are available to all tests.

These methods can be imported into tests using the following, assuming the test module is within the `tests` directory:

```python
from tests import expect_message, validate_message, pack, unpack
```

------------------------------------------------------------------------------------------------------------------------

#### `expect_message`

**Method Signature:**
```python
async def expect_message(transport: BaseTransport, timeout: int) -> bytes
```

**Description:** `expect_message` takes a `transport` and `timeout` and waits a given number of seconds for a message to
be received over the transport. If no message is received, the test containing the call will fail. If a message is
received, the message bytes are returned to the caller.

------------------------------------------------------------------------------------------------------------------------

#### `validate_message`

**Method Signature:**
```python
def validate_message(expected_attrs: [str], msg: Message)
```

**Description:** `validate_message` checks a `Message` object (essentially a python dictionary) for a given set of keys,
failing if an expected key is missing.

**Example:**
```python
    validate_message(
        [
            '@type',
            'label',
            'key',
            'endpoint'
        ],
        invite_msg
    )
```

------------------------------------------------------------------------------------------------------------------------

#### `pack`

**Method Signature:**
```python
async def pack(wallet_handle: int, my_vk: str, their_vk: str, msg: Message) -> bytes
```

**Description:** `pack` packs a message using the Indy-SDK `crypto.pack_message` and is wrapped here for convenience.

------------------------------------------------------------------------------------------------------------------------

#### `unpack`

**Method Signature:**
```python
async def unpack(wallet_handle: int, wire_msg_bytes: bytes, **kwargs) -> Message
```

**Description:** `unpack` unpacks a message using the Indy-SDK `crypto.unpack_message`. Optionally, two keyword
arguments can be specified to verify that the expected "from" and "to" verification keys were used to pack the message.
The method will fail if the expected keys are not found.

**Example:**
```python
    response = await unpack(wallet_handle, response_bytes, expected_to_vk=my_vk, expected_from_vk=their_vk)
```
------------------------------------------------------------------------------------------------------------------------

Defining Features
-----------------

Logical grouping of functionality or "features" help to concisely state the capabilities of an agent. Tests in the Test
Suite are grouped as "features" in python modules (`my_feature.py` is a python module). Metadata about these features as
well as information crucial to test discovery and selection are stored in `features.toml`. Below is an example of what the
`features.toml` file might look like:

```toml
[[feature]]
name="connection.manual"
paths=["tests/connection/manual.py"]
description="""

This feature tests the connection protocol using a user input driven method.

See this document for more details:
https://github.com/hyperledger/indy-hipe/blob/a580d00be443990dfcbcf12be5ac85808340de1f/text/connection-protocol/README.md

"""

[[feature]]
name="my.feature"
paths=["tests/my/feature.py"]
description="""

This is a description of my feature.

"""
```

Each feature has three basic components; the `name`, list of `paths` to the python modules containing tests matching
this feature, and a `description` which gives some human readable information about the feature with, potentially, links
to resources to see more details.
