""" Test Suite fixture definitions.

    These fixtures define the core functionality of the testing agent.

    For more information on how pytest fixtures work, see
    https://docs.pytest.org/en/latest/fixture.html#fixture
"""

import asyncio
import json
import os
import logging

import pytest
from indy import crypto, wallet
from config import Config
from transport.http_transport import HTTPTransport

@pytest.fixture(scope='session')
def event_loop():
    """ Create a session scoped event loop.

        pytest.asyncio plugin provides a default function scoped event loop
        which cannot be used as a dependency to session scoped fixtures.
    """
    return asyncio.get_event_loop()

@pytest.fixture(scope='session')
async def config():
    """ Gather configuration and initialize the wallet.
    """
    DEFAULT_CONFIG_PATH = 'config.toml'
    print('\n\nLoading test configuration from file: {}'.format(DEFAULT_CONFIG_PATH))

    config = Config.from_file(DEFAULT_CONFIG_PATH)
    parser = Config.get_arg_parser()

    args = parser.parse_args()
    if args:
        config.update(vars(args))

    yield config

    # TODO: Cleanup?

@pytest.fixture(scope='session')
def logger(config):
    """ Test logger
    """
    logger = logging.getLogger()
    logger.setLevel(config.log_level)
    return logging.getLogger()



@pytest.fixture(scope='session')
async def wallet_handle(config, logger):
    # Initialization steps
    # -- Create wallet
    logger.debug('Creating wallet: {}'.format(config.wallet_name))
    try:
        await wallet.create_wallet(
            json.dumps({
                'id': config.wallet_name,
                'storage_config': {
                    'path': config.wallet_path
                }
            }),
            json.dumps({'key': 'test-agent'})
        )
    except:
        pass

    # -- Open a wallet
    logger.debug('Opening wallet: {}'.format(config.wallet_name))
    wallet_handle = await wallet.open_wallet(
        json.dumps({
            'id': config.wallet_name,
            'storage_config': {
                'path': config.wallet_path
            }
        }),
        json.dumps({'key': 'test-agent'})
    )

    yield wallet_handle

    # Cleanup
    if config.clear_wallets:
        logger.debug("Closing wallet")
        await wallet.close_wallet(wallet_handle)
        logger.debug("deleting wallet")
        await wallet.delete_wallet(
            json.dumps({
                'id': config.wallet_name,
                'storage_config': {
                    'path': config.wallet_path
                }
            }),
            json.dumps({'key': 'test-agent'})
        )

        logger.debug("removing wallet directory")
        os.rmdir(config.wallet_path)


@pytest.fixture(scope='session')
async def transport(config, event_loop, logger):
    """ Transport fixture.

        Initializes the transport layer.
    """
    MSG_Q = asyncio.Queue()
    if config.transport == "http":
        transport = HTTPTransport(config, logger, MSG_Q)
    else:
        transport = None

    logger.debug("Starting transport")
    event_loop.create_task(transport.start_server())
    return transport

@pytest.fixture(scope='session')
async def connection(config, wallet_handle, transport):
    from tests.connection.manual import get_connection_started_by_suite

    yield await get_connection_started_by_suite(config, wallet_handle, transport)

### Test configuration loading ###

def pytest_ignore_collect(path, config):
    """ Only load tests from feature definition file. """
    if path.ext != ".toml":
        return True
    return False

def pytest_runtest_makereport(item, call):
    """ Customize report printing. """
    from _pytest.runner import TestReport, ExceptionInfo, skip
    when = call.when
    duration = call.stop - call.start
    keywords = {x: 1 for x in item.keywords}
    excinfo = call.excinfo
    sections = []
    if not call.excinfo:
        outcome = "passed"
        longrepr = None
    else:
        if not isinstance(excinfo, ExceptionInfo):
            outcome = "failed"
            longrepr = excinfo
        elif excinfo.errisinstance(skip.Exception):
            outcome = "skipped"
            r = excinfo._getreprcrash()
            longrepr = (str(r.path), r.lineno, r.message)
        else:
            outcome = "failed"
            if call.when == "call":
                longrepr = item.repr_failure(excinfo)
            else:  # exception in setup or teardown
                longrepr = item._repr_failure_py(
                    excinfo, style=item.config.option.tbstyle
                )
    for rwhen, key, content in item._report_sections:
        sections.append(("%s %s" % (key, rwhen), content))
    return TestReport(
        item.nodeid,
        item.location,
        keywords,
        outcome,
        longrepr,
        when,
        sections,
        duration,
        user_properties=item.user_properties,
        )

def pytest_collect_file(path, parent):
    """ Customize test collection. """
    if path.ext == ".toml" and path.basename.startswith("features"):
        return TomlTestDefinitionFile(path, parent)

class TomlTestDefinitionFile(pytest.File):
    """ Test collection from Toml file. """
    def collect(self):
        import toml # we need a toml parser

        default_config_path = "config.toml"
        conf = toml.load(default_config_path)
        tests = toml.load(self.fspath.open())
        for test in tests['feature']:
            if test['name'] in conf['tests']:
                yield Feature(self, test['name'], test['paths'], test['description'])


class Feature(pytest.Collector):
    """ A Pytest collector representing a feature. Features collect one or many
        FeatureParts.
    """
    def __init__(self, parent, name, paths, description):
        super(Feature, self).__init__(name, parent=parent)
        self.parent = parent
        self.name = name
        self.paths = paths
        self.description = description
        self.test_failed = False
        self.items = []

    def collect(self):
        for path in self.paths:
            self.items.append(FeaturePart(self, self.name, path))
        yield from self.items

    def last_part(self):
        """ Return last item. """
        if not self.items:
            return None
        return self.items[-1]


class FeaturePart(pytest.Module):
    """ A Part of a Feature. FeatureParts are python modules where test functions are defined.
    """
    def __init__(self, parent, name, path):
        super(FeaturePart, self).__init__(path, parent=parent)
        self.name = '{}.{}'.format(name, path)
        self._nodeid = name
        self.items = []

    def collect(self):
        self.items = super(FeaturePart, self).collect()
        for item in self.items:
            if isinstance(item, pytest.Function):
                yield FeatureTestFunction(self.name, item)
            else:
                yield item

    def last_child(self):
        """ Return last item. """
        if self.parent.last_part() != self:
            return None
        if not self.items:
            return None

        return self.items[-1]

    @property
    def description(self):
        """ Return description of Feature. """
        return self.parent.description

    @property
    def test_failed(self):
        """ Return whether Feature has failed a test or not. """
        return self.parent.test_failed

    @test_failed.setter
    def test_failed(self, val):
        self.parent.test_failed = val

class FeatureTestFunction(pytest.Function):
    """ A wrapper around Pytest Functions returned from Module collector.
        Enables better reporting from tests.
    """

    def __init__(self, feature, func):
        self.feature = feature
        self.func = func

    def __getattribute__(self, name):
        """ A bit of a hack to easily wrap pytest Function. """
        try:
            attr = object.__getattribute__(self, name)
        except AttributeError:
            attr = self.func.__getattribute__(name)

        return attr

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if not self.parent.test_failed:
            self.parent.test_failed = True

        if self.parent.test_failed and self.parent.last_child() == self.func:
            self.add_report_section(self.feature, "Feature Description:", self.parent.description)

        return self._repr_failure_py(excinfo, style="long")

    def reportinfo(self):
        return self.fspath, 0, "Feature: %s, Test: %s" % (self.feature, self.name)
