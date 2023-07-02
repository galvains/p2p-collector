import asyncio
import random
import argparse

from loguru import logger
import collectors.launcher as launcher

logger.add('debug.log', format='{time} | {level} | {message}', level='DEBUG',
           rotation='5 mb', compression='zip')

parser = argparse.ArgumentParser()
parser.add_argument('-tc', '--tcount', type=int, required=True, help='Count of threads')
parser.add_argument('-d', '--delay', type=int, nargs=2, default=[30, 35], help='The spread of the delay between laps')
args = parser.parse_args()


async def startup():
    await launcher.loader(threads_count=args.tcount, delay=random.randint(args.delay[0], args.delay[1]))


if __name__ == '__main__':
    asyncio.run(startup())
