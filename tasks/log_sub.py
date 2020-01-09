import ujson
from models.admin import SysLog


# redis 日志订阅
async def log_sub(channel):
    async for message in channel.iter():
        print(message)
        data = ujson.loads(message.decode())
        val = data.pop('username')
        data.update(dict(name=val))
        new_log = SysLog(**data)
        await new_log.save()
