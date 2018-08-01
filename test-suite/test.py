""" Execute the Agent Test Suite.

    This file is used to bootstrap into pytest, executing tests that are
    specified in the config file.
"""
import pytest
from config import Config

DEFAULT_CONFIG_PATH = 'test_config.toml'

config = Config.from_file(DEFAULT_CONFIG_PATH)

tests = [ ''.join(['tests/', test.replace('.','/')]) for test in config.tests ]

pytest.main(tests)
