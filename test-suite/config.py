""" Module for storing and updating configuration.
"""

from typing import Optional
import toml
import argparse

class InvalidConfigurationException(Exception):
    """ Exception raise on absent required configuration value
    """
    pass


class StoreDictKeyPair(argparse.Action):
     def __init__(self, option_strings, dest, nargs=None, **kwargs):
         self._nargs = nargs
         super(StoreDictKeyPair, self).__init__(option_strings, dest, nargs=nargs, **kwargs)
     def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         for kv in values:
             k,v = kv.split("=")
             my_dict[k] = v
         setattr(namespace, self.dest, my_dict)


# TODO: Make adding new configuration options less repetetive. There is a lot of
# duplicate code here.

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
            '--config',
            metavar="KEY=VAL",
            dest='config',
            action=StoreDictKeyPair,
            nargs='+',
            help='A space separated list of Key-Value pairs.'
        )
        return parser

    @staticmethod
    def from_file(config_path):
        conf = Config()
        conf.load_config(config_path)
        return conf

    def __init__(self):
        self.wallet_name: Optional[str] = None
        self.wallet_path: Optional[str] = None
        self.clear_wallets: Optional[Bool] = None
        self.tests: Optional[List[str]] = None

    def load_config(self, config_path):
        """ Load configuration from a toml file with a given path.
        """

        config_dict = toml.load(config_path)

        if 'config' not in config_dict:
            raise InvalidConfigurationException()

        if 'wallet_name' in config_dict['config']:
            self.wallet_name = config_dict['config']['wallet_name']
        
        if 'wallet_path' in config_dict['config']:
            self.wallet_path = config_dict['config']['wallet_path']

        if 'clear_wallets' in config_dict['config']:
            self.clear_wallets = config_dict['config']['clear_wallets']

        if 'tests' in config_dict['config']:
            self.tests = config_dict['config']['tests']
        else:
            self.tests = ['core']

    def update_config_with_args_dict(self, args):
        """ Update the configuration using command line arguments.
            This typically called after loading a configuration file using
            load_config
        """

        if 'wallet_name' in args:
            self.wallet_name = args['wallet_name']

        if 'wallet_path' in args:
            self.wallet_path = args['wallet_path']

        if 'clear_wallets' in args:
            self.clear_wallets = args['clear_wallets']

        if 'tests' in args:
            self.tests = args['tests']
        else:
            self.tests = ['core']


if __name__ == '__main__':

    DEFAULT_CONFIG_PATH = 'config.toml'

    print("TESTING CONFIGURATION")
    parser = Config.get_arg_parser()
    config = Config.from_file(DEFAULT_CONFIG_PATH)
    print(config.wallet_path, config.clear_wallets, config.tests)

    args = parser.parse_args()
    print(args)
    if args.config is not None:
        config.update_config_with_args_dict(args.config)

    print(config.wallet_path, config.clear_wallets, config.tests)
