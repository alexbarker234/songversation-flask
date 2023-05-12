# expanded upon https://dev.to/matteo/async-request-with-python-1hpo
async def fetch(session, url, data):
    """Execute an http call async
    Args:
        session: context for making the http call
        url: URL to call
        data: optional, additional data attached to the call
    Return:
        A dictionary containing 'url', 'json' dictionary of response & additional data attached to the call
    """ 
    async with session.get(url) as response:
            resp = await response.json()
            return { 'url': url, 'json': resp, 'data': data }