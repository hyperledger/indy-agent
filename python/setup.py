
from distutils.core import setup

setup(
    name='python3-indy-agent',
    version='0.1',
    url='https://github.com/hyperledger/indy-agent',
    license='MIT/Apache-2.0',
    description='Reference Agent for the Indy-SDK',
    install_requires=['python3-indy', 'aiohttp', 'serpy', 'aiohttp-index']
)
