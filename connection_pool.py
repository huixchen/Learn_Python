import aiomysql
import logging
import asyncio


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
        await cur.execute(sql.replace('?', '%s'), args or ())
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
async def execute(sql, args):
    log(sql)
    with (await __pool) as conn:
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            # the amount of affected
            await cur.close()
        except BaseException as e:
            raise
        return affected
