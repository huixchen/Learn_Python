import asyncio
from coroweb import get, post
from model import User, Blog, Comment, next_id
from aiohttp import web
import json
import time, re, hashlib
from apis import APIError, APIValueError, APIPermissionError, APIResourceNotFoundError, Page
from config import configs
import logging


COOKIE_NAME = "awesession"
# to name in set_cookie
_COOKIE_KEY = configs.session.secret


def user2cookie(user, max_age):
    expires = str(time.time()+max_age)
    s = "{}-{}-{}-{}".format(user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode("utf-8")).hexdigest()]
    return "-".join(L)


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


_RE_EMAIL = re.compile(r"^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$")
_RE_SHA1 = re.compile(r"^[0-9a-f]{40}$")


@post("/api/users")
async def api_register_user(*, name, email, passwd):
    if not name or not name.strip():
        raise APIValueError("name")
    if not email or not _RE_SHA1.match(passwd):
        raise APIValueError("email")
    if not passwd and not _RE_SHA1.match(passwd):
        raise APIValueError("password")
    users = await User.findAll(where="email=?", args=[email])
    # check whether the email has been registered
    if len(users) > 0:
        raise APIError("register failed", "email", "Email is already in use")
    uid = next_id()
    sha1_passwd = "{}:{}".format(uid, passwd)
    user = User(id=uid, name=name.strip(), email=email,
                passwd=hashlib.sha1(sha1_passwd.encode("utf-8")).hexdigest(),
                image="http://www.gravatar.com/avatar/{}?d=mm&s=120".format(
                    hashlib.md5(email.encode("utf-8")).hexdigest()))
    await user.save()
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400),
                 max_age=86400, httponly=True)
    user.passwd = "*******"
    r.content_type = "application/json"
    r.body = json.dumps(user, ensure_ascii=False).encode("utf-8")
    return r


@get('/')
async def handler_url_blog(request, *, page='1'):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,
        'user': request.__user__,
        'page': p,
    }


@get('/users')
async def handler_url_users(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }


@get('/register')
def register(request):
    return {
        "__template__": "register.html"
    }


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email')
    if not passwd:
        raise APIValueError('password', 'Invalid password')
    users = await User.findAll(where='email=?', args=[email])
    if len(users) == 0:
        raise APIValueError('email', 'Email does not exist')
    user = users[0]
    sha1 = hashlib.sha1('{}:{}'.format(user.id, passwd).encode('utf-8'))
    # sha1.update(user.id.encode('utf-8'))
    # sha1.update(b':')
    # sha1.update(passwd.encode('utf-8'))
    if sha1.hexdigest() != user.passwd:
        raise APIValueError('password', 'invalid password')
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400),
                 max_age=86400, httponly=True)
    user.passwd = '*******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if float(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '{}-{}-{}-{}'.format(uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = "******"
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.del_cookie(COOKIE_NAME)
    logging.info('user signed out and redirected to {}'.format(referer))
    return r


@post('/api/blogs')
async def api_create_blogs(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name should not be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary should not be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content should not be empty')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name,
                user_image=request.__user__.image, summary=summary.strip(),
                name=name.strip(), content=content.strip())
    await blog.save()
    return blog


@get('/manage/blogs/create')
def manage_create_blog(request):
    check_admin(request)
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs',
        'user': request.__user__,
    }



def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    logging.info('this is limiiiiiiiiiiiiiit {}'.format(p.limit))
    return dict(page=p, blogs=blogs)


@get('/manage/blogs')
def manage_blogs(*, page='1',request):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page),
        'user': request.__user__,
    }


@get('/manage/blogs/edit')
def manage_blogs_edit(*, id=1, request):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/{}'.format(id),
        'user': request.__user__,
    }


@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    blog = await Blog.find(id)
    return blog


@post('/api/blogs/{id}/delete')
async def api_delete_blog(*, id, request):
    check_admin(request)
    r = await Blog.find(id)
    r = await r.remove()
    return dict(id=id)


@get('/blog/{id}')
async def get_blog(request, *, id):
    blog = await Blog.find(id)
    comments = await Comment.findAll(where='blog_id=?', args=[blog.id])
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'user': request.__user__,
        'comments': comments,
    }


@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    blog = await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('blog')
    if not content or not content.strip():
        raise APIValueError('content')
    if not request.__user__:
        raise APIPermissionError('Please sign first')
    comment = Comment(blog_id=blog.id, user_id=request.__user__.id,
                      user_image=request.__user__.image, content=content,
                      created_at=time.time(), user_name=request.__user__.name)
    await comment.save()
    return comment


@get('/api/comments')
async def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = await Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)
