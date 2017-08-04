import asyncio
from coroweb import get, post


@get('/')
async def handler_url_blog(request):
    body = '<h1>A</h1>'
    return body

@get('/greeting')
async def handler_url_greeting(*, name, request):
    body = '<h1>aaa: /greeting {}</h1>'.format(name)
    return body
