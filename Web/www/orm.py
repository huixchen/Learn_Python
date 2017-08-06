#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# http://www.songluyi.com/python-%E7%BC%96%E5%86%99orm%E6%97%B6%E7%9A%84%E9%87%8D%E9%9A%BE%E7%82%B9%E6%8E%8C%E6%8F%A1/
# 可做参考
import asyncio, logging
import aiomysql


def log(sql, args=()):
    logging.info('SQL:{}'.format(sql))


async def create_pool(loop, **kw):
    # create connection pool, it can be used to store information
    # and http would not need to open the database everytime
    # it is connected
    # This understanding can be WRONG!!
    logging.info('create database connection pool')
    # create one global variable as __pool via aiomysql's function
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )


# define select syntax, we will pass in sql statement and args
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        # return cursor as dict
        await cur.execute(sql.replace('?', '%s'), args)
        # sql's placeholder is `?` while it is `%s` for mysql
        # the replace function would replace it automately
        # standard api of aiomysql,
        # execute(query, args=None)
        if size:
            rs = await cur.fetchmany(size)
            # return only size of rows
        else:
            rs = await cur.fetchall()
            # return all rows
        await cur.close()
        logging.info('rows returned: {}.'.format(len(rs)))
    return rs


# define insert, update, delete
# the three are similar so we can just define one function
#async def execute(sql, args, autocommit=True):
#    log(sql)
#    async with (await __pool) as conn:
#        if not autocommit:
#            await conn.begin()
#        try:
#            cur = await conn.cursor()
#            await cur.execute(sql.replace('?', '%s'), args)
#            affected = cur.rowcount
#            # the amount of affected
#            await cur.close()
#        except BaseException as e:
#            raise
#        finally:
#            conn.close()
#        return affected

async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected

def create_args_string(num):
    l = []
    for n in range(num):
        l.append('?')
    return ', '.join(l)

async def close_pool():
    logging.info('close database connection pool...')
    global __pool
    if __pool is not None:
        __pool.close()
        await __pool.wait_closed()

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '{}, {}:{}'.format(self.__class__.__name__,
                                  self.column_type, self.name)


class StringField(Field):

    def __init__(self, name=None, primary_key=False,
                 default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bright', primary_key, default)
        # call the init function of `Filed`, let the name be inputed name,
        # column_type = 'bright'


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class ModelMetaclass(type):

    def __new__(cls, name, base, attrs):
        # __new__ is the function to create class
        # __init__ is the function to create instance
        if name == 'Model':
            return type.__new__(cls, name, base, attrs)
        tableName = attrs.get('__table__', None) or name
        logging.info('found model {}, tableName {}'.format(name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mapping {} ==> {}'.format(k, v))
                mappings[k] = v
                if v.primary_key:
                    logging.info('found primarykey {}'.format(k))
                    # find the primary key
                    if primaryKey:
                        # if there is already one existed primary key
                        raise RuntimeError(
                            'Duplicate primary key found for field'.format(k))
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key did not find')
        for k in mappings.keys():
            attrs.pop(k)
            # find the attrs in the cls that is going to be built and store its
            # attrs into one mappings dict.
            # then remove the attrs from cls is going to be built
            # because when we create instance, if the instance have same name
            # property as class, the class's property would be shadowed.
            # could be WRONG!!!
        escaped_fields = list(map(lambda f: '`{}`'.format(f), fields))
        # ``(backticks) here are for sql statement to avoid table name or
        # things like this are named as select or similarly
        # primaryKey do not need to add this because you donot want to print out
        # your primary key with backticks surrounded.
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'] = fields
        attrs['__select__'] = 'select `{}`, {} from {}'.format(
            primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `{}` ({}, `{}`) values ({})'.format(
            tableName, ', '.join(escaped_fields), primaryKey,
            create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `{}` set {} where `{}` = ?'.format(
            tableName, ', '.join(map(lambda f: '`{}`=?'.format(
                mappings.get(f).name or f), fields)),
            primaryKey)
        attrs['__delete__'] = 'delete from `{}` where `{}`=?'.format(
            tableName, primaryKey)
        return type.__new__(cls, name, base, attrs)


class Model(dict, metaclass=ModelMetaclass):
    # Inherit form class dict

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
        # about super
        # http://wiki.jikexueyuan.com/project/explore-python/Class/super.html

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                r"'Model' object has no attribute '{}'".format(key))

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)
        # the None means if there is not such one key, it would return None, it
        # can also be set as other value
        # also notice that there is no underline in getattr

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                # if there is no value for the key,
                # call the `Field` type and use its default value
                value = (field.default() if callable(field.default)
                         else field.default)
                logging.debug(
                    'Using default value for {}: {}'.format(key, str(value)))
                setattr(self, key, value)
        return value

    # use @classmethod to create class function
    # so for class User(Model), I can call the find function in follow way:
    # User.find('132')
    @classmethod
    async def find(cls, pk):
        # find object by primary key
        rs = await select('{} where `{}`=?'.format(
            cls.__select__, cls.__primary_key__),
            [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        # args = list(map(self.getValueOrDefault, self.__fields__))
        args = []
        for key in self.__fields__:
            args.append(self.getValueOrDefault(key))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn(
                'failed to insert rows,affected rows: {}'.format(rows))

    async def update(self):
        sql = self.__update__
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        affected = await execute(sql, args)
        if affected != 1:
            logging.warn('failed to update, updated {} rows'.format(affected))

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        logging.info('this is where {}'.format(where))
        logging.info('this is args {}'.format(args))
        sql = cls.__select__
        # it is function of the class, so it should be cls.__select__ instead of
        # self.__select__
        if where:
            sql = sql + ' where ' + where
            # the origin method used here is use list to add together and join
            # the list which could be better, the mistake i made was i did not
            # add space around the `where`, `order` etc.
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql = sql + ' order by ' + orderBy
        limit = kw.get(' limit', None)
        # dict 提供get方法 指定放不存在时候返回后学的东西 比如a.get('Fuck',None)
        if limit is not None:
            sql = sql + ' limit '
            if isinstance(limit, int):
                sql = sql + ' ? '
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql = sql + ' ? ' * 2
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: {}'.format(str(limit)))
        logging.info('this is findAAAAAAAAAAAAAAL sql {}'.format(sql))
        rs = await select(sql, args)
        return [cls(**r) for r in rs]

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        sql = self.__delete__
        affected = await execute(sql, args)
        if affected != 1:
            logging.warn(
                'failed to remove, affected row: {}'.format(len(affected)))

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        sql = 'select {} _num_ from {}'.format(selectField, cls.__table__)
        # _num_ here is as the same to `as _num_'
        if where:
            sql = sql + 'where' + where
        rows = await select(sql, args, 1)
        if len(rows) == 0:
            return None
        return rows[0]['_num_']
