import functools
import inspect
from asyncio import web


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
                elif (ct.startwith('application/x-www-form-urlencoded') or
                      ct.startwith('multipart/form-data')):
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
