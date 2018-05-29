""" Handlers for web interface endpoints.
"""

# pylint: disable=import-error

import aiohttp_jinja2

@aiohttp_jinja2.template('index.html')
def index(request):
    """ Handler for GET /

        Uses template index.html
    """
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

# Not sure if this is needed and it's causing problems
# with pylint. Commenting out for now.
#@aiohttp_jinja2.template('index.html')
#def request(request):
#    return {}


#@aiohttp_jinja2.template('index.html')
#def connections(request):
#    """ Return list of made connections.
#    """
#    pass

#@aiohttp_jinja2.template('index.html')
#def requests(request):
#    """ Return list of received requests.
#    """
#    print("handling requests")
#    reqs = request.app['agent'].received_requests
#    return {}


#@aiohttp_jinja2.template('index.html')
#def response(request):
#    print("handling response")
#    return {}
