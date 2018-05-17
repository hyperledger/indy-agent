import aiohttp
from aiohttp import web

def require_init(agent):
    if not agent.initialized:
        raise web.HTTPFound('/init')
