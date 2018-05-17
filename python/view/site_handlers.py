import aiohttp_jinja2

@aiohttp_jinja2.template('index.html')
def index(request):
    return {}