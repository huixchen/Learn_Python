import os
import functools
import inspect
from asyncio import web
from urllib import parse
import logging
import asyncio


def get_params(fn):
    return inspect.signature(fn).parameters


# use inspect module to obtain the relationship between URL handle function and
# arguments of request.
def get_required_kw_args(fn):
    # obtin keywords parameters have not default value
    args = []
    params = get_params(fn)
    # use inspect to check the function, its parameters would be stored in
    # OrderedDict
    for name, param in params.items():
        if (str(param.kind) == 'KEYWORD_ONLY'
                and param.default == inspect.Parameter.empty):
            # https://docs.python.org/3.6/library/inspect.html#inspect.Parameter.kind
            # http://www.imooc.com/article/13053
            # for function, if there is one `*, ` `*args`,
            # in parameters, parameters
            # after the `*` would all be keyword only
            # inspect.Parameter.empty is one class, if the param have no default
            # value, param.default would return the class.
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    # obtain keywords parameters
    params = get_params(fn)
    args = []
    for name, param in params.items():
        if str(param.kind) == 'KEYWORD_ONLY':
            args.append(name)
    return tuple(args)


def has_named_kw_arg(fn):
    # tell whether there is one keyword parameters
    params = get_params(fn)
    for name, param in params.items():
        if str(param.kind) == 'KEYWORD_ONLY':
            return True


def has_var_kw_arg(fn):
    # tell whether there is var_keyword
    # var_keyword means **kwargs (a dict of keyword argument)
    params = get_params(fn)
    for name, param in params.items():
        if str(param.kind) == 'VAR_KEYWORD':
            return True


def has_request_arg(fn):
    # tell whether there is one parameter named as `request` and is the last
    # named parameter
    params = get_params(fn)
    sig = inspect.signature(fn)
    found = False
    for name, param in params:
        if name == 'request':
            found = True
            continue
            # end this loop and goes to the next loop, which means would check
            # the following name and param in params
        if (found and str(param.kind) not in
                ['VAR_POSITIONAL', 'KEYWORD_ONLY', 'VAR_KEYWORD']):
            raise ValueError(
                'request parameter must be the last named\
                parameter in function: {}{}'.format(fn.__name__, str(sig)))
            # it means if the parameter after 'request' is neither the three
            # one, it should be `POSITIONAL_OR_KEYWORD`, and it means
            # request is not the last named parameter
            # although I am a little confused why not just say it is
            # `POSITIONAL_OR_KEYWORD`, one potential reason is that there is
            # another kind of parameter, although it has been few used now
        return True


def get(path):
    # define decorator @get('/path')
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        # what here did is just give function `wrapper` one attribute
        # `__method__` and its value is `GET`
        # but Why?
        # This understanding could be WRONG!!!
        wrapper.__route__ = path
        return wrapper
    return decorator


def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_arg = has_named_kw_arg(fn)
        self._named_kw_arg = get_named_kw_args(fn)
        self._get_required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        # a little confused about what request is
        # and where does the function like `content_type`, `json` from
        kw = None
        if (self._has_var_kw_arg or self._has_named_kw_arg
                or self.get_required_kw_args):
            if request.method == 'POST':
                if not request.content_type:
                    # tell whether there is content-type, normally content-type
                    # could include value of text/html, charset:utf-8
                    # https://github.com/KaimingWan/PureBlog/blob/master/www/web_frame.py
                    return web.HTTPBadRequest(text='Missing content-type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    # application/json as response head tell server that the
                    # information body is JSON object
                    params = await request.json()
                    # read request body decode as json
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest(
                            text='JSON body must be object')
                    kw = params
                elif (ct.startswith('application/x-www-form-urlencoded') or
                      ct.startswith('multipart/form-data')):
                    # `application/x-www-form-urlencoded` - most normal POST
                    # method, if we do not set <form> enctype propery, it would
                    # be sent in this way
                    # WTF is enctype??
                    # `multipart/form-data` - if we set `enctype`, it would be
                    # sent in this way
                    # more information:
                    # https://imququ.com/post/four-ways-to-post-data-in-http.html
                    params = await request.post()
                    # use decorator?
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest(
                        text='Unsupported content-type {}'.format(
                            request.content_type))
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        # parse.parse_qs parse a query string argument (data
                        # type of application/x-www-form-urlencoded), data are
                        # returned in form of dict, the dict keys are the unique
                        # query variable names and the values are lists of
                        # values for each name.
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
            # match_info would return one dict and all keyword only parameters
            # obtained from request would be stored in this dict.
        else:
            if not self._has_var_kw_arg and self._named_kw_arg:
                # if there is not variable keyword but there is named keyword
                # WHY?
                copy = dict()
                for name in self._named_kw_arg:
                    # remove all the unnamed kw
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named'
                                    'arg and kw args: {}'.format(k))
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        if self._get_required_kw_args:
            for name in self._get_required_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest('Missing argument'
                                              '{}'.format(name))
        logging.info('call with args: {}'.format(str(kw)))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    # app is one object within aiohttp module
    logging.info('add static {} => {}'.format('/static/', path))


def add_route(app, fn):
    # one simple URL handler function
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in {}'.format(str(fn)))
    if not asyncio.iscoroutine(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
        # estimate the function to see whether it is coroutine function or
        # generator
        # if neither, change it to one coroutine
    logging.info('add route {} {} => {} ({})'.format(
        method, path, fn.__name__,
        ','.join(inspect.signature(fn).parameters.key())))
    app.router.add_route(method, path, RequestHandler(app, fn))
    # because RequestHandler has function `__call__`, it is callable and since
    # can be viewed as one handler


def add_routes(app, module_name):
    n = module_name.rfind('.')
    # rfind would return where is the character last appear, if it did not
    # appear, it would return -1
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name
        mod = getattr(__import__(module_name[:n], globals(), locals(),
                                 [name], 0), name)
        # ergodic the imported module to get function, because we used decorator
        # @post and @get, there would be attribute `__method__` and `__route__`
        # assume we the module name is `aaa.bbb`, `bbb` would be function within
        # the module `aaa`, we only need to import the module `aaa`
        for attr in dir(mod):
            # dir() return attributes of module
            if attr.startswith('_'):
                continue
            fn = getattr(mod, attr)
            if callable(fn):
                method = getattr(fn, '__method__', None)
                path = getattr(fn, '__route__', None)
                if method and path:
                    add_route(app, fn)
