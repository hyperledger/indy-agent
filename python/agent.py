""" Module defining Agent class and related methods
"""
import json
from indy import wallet, did, error

class WalletConnectionException(Exception):
    pass

class Agent:
    """ Agent class storing all needed elements for agent operation.
    """
    def __init__(self):
        self.owner = None
        self.wallet_handle = None
        self.endpoint = None
        self.endpoint_vk = None
        self.ui_token = None
        self.pool_handle = None
        self.ui_socket = None
        self.initialized = False
        self.modules = []

    async def connect_wallet(self, agent_name, passphrase, ephemeral=False):
        """ Create if not already exists and open wallet.
        """

        self.owner = agent_name
        wallet_suffix = "wallet"
        if ephemeral:
            wallet_suffix = "ephemeral_wallet"
        wallet_name = '{}-{}'.format(self.owner, wallet_suffix)

        wallet_config = json.dumps({"id": wallet_name})
        wallet_credentials = json.dumps({"key": passphrase})

        # Handle ephemeral wallets
        if ephemeral:
            try:
                await wallet.delete_wallet(wallet_config, wallet_credentials)
                print("Removing ephemeral wallet.")
            except error.IndyError as e:
                if e.error_code is error.ErrorCode.WalletNotFoundError:
                    pass  # This is ok, and expected.
                else:
                    print("Unexpected Indy Error: {}".format(e))
            except Exception as e:
                print(e)
        # pylint: disable=bare-except

        try:
            await wallet.create_wallet(wallet_config, wallet_credentials)
        except error.IndyError as e:
            if e.error_code is error.ErrorCode.WalletAlreadyExistsError:
                pass # This is ok, and expected.
            else:
                print("Unexpected Indy Error: {}".format(e))
        except Exception as e:
            print(e)

        try:
            self.wallet_handle = await wallet.open_wallet(
                wallet_config,
                wallet_credentials
            )

            (_, self.endpoint_vk) = await did.create_and_store_my_did(self.wallet_handle, "{}")

            self.initialized = True

        except Exception as e:
            print(e)
            print("Could not open wallet!")

            raise WalletConnectionException
