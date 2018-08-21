import asyncio
import time
import aioredis
import random

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

loop = asyncio.get_event_loop()
RECORDS = 86000

async def add_message_with_sleep(redis, loop, stream):
    start = time.time()
    records = RECORDS + 1
    for _ in range(records):
        temperature = str(random.randrange(20, 30))
        humidity = str(random.randrange(10, 20))
        fields = {'temperature': temperature.encode('utf-8'),
                  'humidity': humidity.encode('utf-8')}
        await redis.xadd(stream, fields)
    end = time.time()
    print(f"Inserting {RECORDS} records took {end - start} seconds")

async def main():
    redis = await aioredis.create_redis('redis://localhost', loop=loop)
    stream = 'chennai'
    await add_message_with_sleep(redis, loop, stream)
    redis.close()
    await redis.wait_closed()

loop.run_until_complete(main())
