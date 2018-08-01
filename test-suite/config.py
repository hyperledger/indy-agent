""" Module for storing and updating configuration.
"""

import typing
from typing import Optional, Dict, Any
import toml
import argparse
import os

class InvalidConfigurationException(Exception):
    """ Exception raise on absent required configuration value
    """
    pass


class Config():
    """ Configuration class used to store and update configuration information.
    """

    @staticmethod
    def get_arg_parser():
        """ Construct an argument parser that matches our configuration.
        """
        parser = argparse.ArgumentParser(
            description='Run Indy Agent Test Suite'
        )
        parser.add_argument(
            '-s',
            '--source',
            dest='host',
            metavar='ADDR',
            type=str,
            help='Set the test agent\'s source addres to ADDR'
        )
        parser.add_argument(
            '-p',
            '--source-port',
            dest='port',
            metavar='PORT',
            type=int,
            help='Set the port that the test agent will listen on to PORT'
        )
        parser.add_argument(
            '-t',
            '--tested-agent',
            metavar='URL',
            dest='tested_agent',
            type=str,
            help='The url of the tested agent'
        )
        parser.add_argument(
            '-wn',
            '--wallet-name',
            dest='wallet_name',
            metavar='WALLET_NAME',
            type=str,
            help='Set the name used for the test agent\'s wallet to WALLET_NAME'
        )
        parser.add_argument(
            '-wp',
            '--wallet-path',
            metavar='WALLET_PATH',
            dest='wallet_path',
            type=str,
            help='Set the directory that the test agent\'s wallet will be stored in to WALLET_PATH'
        )
        parser.add_argument(
            '-n',
            '--no-clobber',
            dest='clear_wallets',
            action='store_false',
            help='Preserve wallets used for testing. Default behavior is to delete all wallets created by tests.'
        )
        parser.add_argument(
            '--tests',
            metavar='TEST',
            type=str,
            nargs='+',
            help='Space separated list of test names to run. Each test string is the module name for the test.'
        )
        return parser

    @staticmethod
    def from_file(config_path: str):
        conf = Config()
        options = toml.load(config_path)
        conf.update(options)
        return conf

    def __init__(self):
        self.host: str = 'localhost'
        self.port: int = 3000
        self.tested_agent: str = 'http://localhost:3001/indy'
        self.wallet_name: str = 'testing'
        self.wallet_path: str = ''
        self.clear_wallets: bool = True
        self.tests: List[str] = ['core']

    def update(self, options: Dict[str, Any]):
        """ Load configuration from the options dictionary.
        """

        for var in self.__dict__.keys():
            if var in options and options[var] is not None:
                if type(options[var]) is not type(self.__dict__[var]):
                    err_msg = 'Configuration option {} is an invalid type'.format(var)
                    raise InvalidConfigurationException(err_msg)

                self.__dict__[var] = options[var]

        self._wallet_path_post_process()

    def _wallet_path_post_process(self):
        if self.wallet_path is not None and self.wallet_path.strip()[0] is not '/':
            self.wallet_path = os.getcwd() + '/' + self.wallet_path


if __name__ == '__main__':

    DEFAULT_CONFIG_PATH = 'config.toml'

    print("TESTING CONFIGURATION")
    parser = Config.get_arg_parser()
    config = Config.from_file(DEFAULT_CONFIG_PATH)
    print(config.wallet_path, config.clear_wallets, config.tests)

    args = parser.parse_args()
    print(args)
    if args:
        config.update(vars(args))

    print(config.wallet_path, config.clear_wallets, config.tests)
