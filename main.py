import asyncio
import random

import collectors.launcher as launcher


async def startup():
    await launcher.loader(threads_count=3, delay=random.randint(22, 28))


if __name__ == '__main__':
    asyncio.run(startup())
