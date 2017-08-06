import asyncio
from coroweb import get, post
from model import User, Blog
import time


@get('/')
async def handler_url_blog(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

@get('/greeting')
async def handler_url_greeting(*, name, request):
    body = '<h1>aaa: /greeting {}</h1>'.format(name)
    return body

@get('/users')
async def handler_url_users(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
