import sys
import asyncio
import time
import aioredis
import random
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

async def process_message(redis, loop, group, consumer, streams):
    start = time.time()
    records = 0
    while True:
        result = await redis.xread_group(group, consumer, streams, count=1, latest_ids=['>'])
        if result:
            records += 1
            print(f"processing {result}")
            time.sleep(1)
        else:
            print("Timeout")
            break
    end = time.time()
    print(f"Reading {records} records took {end - start} seconds")

async def main(consumer):
    redis = await aioredis.create_redis('redis://localhost', loop=loop)
    streams = ['chennai']
    group = 'mygroup'

    for stream in streams:
        exists = await redis.exists(stream)
        if not exists:
            await redis.xadd(stream, {b'foo': b'bar'})

        try:
            await redis.xgroup_create(stream, group)
        except aioredis.errors.ReplyError as e:
            print("Consumer group already exists")

    await process_message(redis, loop, group, consumer, streams)
    redis.close()
    await redis.wait_closed()

if len(sys.argv) < 2:
    print("Consumer name is required")
    exit(1)

consumer = sys.argv[1]
loop.run_until_complete(main(consumer))
