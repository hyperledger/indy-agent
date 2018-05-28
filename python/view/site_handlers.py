import aiohttp_jinja2
import json

@aiohttp_jinja2.template('index.html')
def index(request):
    print("Handling /")
    agent = request.app['agent']
    conns = agent.connections
    reqs = agent.received_requests
    owner = agent.owner
    first = False
    if owner is None or owner == '':
        owner = 'Default'
        first = True
    return {
                "agent_name": owner,
                "connections": conns,
                "requests": reqs,
                "first": first
            }


@aiohttp_jinja2.template('index.html')
def request(request):
    return {}


@aiohttp_jinja2.template('index.html')
def connections(request):
    pass

@aiohttp_jinja2.template('index.html')
def requests(request):
    print("handling requests")
    reqs = request.app['agent'].received_requests
    return {}


@aiohttp_jinja2.template('index.html')
def response(request):
    print("handling response")
    return {}
