import orm
from model import User, Blog, Comment
import asyncio
from config import configs


async def test():
    await orm.create_pool(loop=loop, **configs.db)

    u = User(name='Tdedafastad', email='dtefasdst@aad', passwd='d12ad31', image='addaa')

    await u.save()
    r = await User.findAll()
    await orm.close_pool()
    print(r)

#async def remove():
#    await orm.create_pool(loop=loop, user='root', password='', db='awesome')
#
#    r = await User.find('00150168181380894a9d4d9c3f44790b92de5917c4fbc38000')
#    await r.remove()
#    print('remove {}'.format(r))
#    await orm.close_pool()
#
#async def update():
#    await orm.create_pool(loop=loop, user='root', password='', db='awesome')
#
#    r = await User.find('001501681395475008028fefa0c44f9b72cc3d178258df6000')
#    r.passwd = 'dafa123333333'
#    await r.update()
#    await orm.close_pool()


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
