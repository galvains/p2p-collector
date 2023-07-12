import asyncio
import random
import argparse
# import yaml

from loguru import logger
import collectors.launcher as launcher

logger.add('debug.log', format='{time} | {level} | {message}', level='DEBUG',
           rotation='5 mb', compression='zip')

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--delay', type=int, nargs=2, default=[30, 35], help='The spread of the delay between laps')
args = parser.parse_args()


async def startup():
    await launcher.loader(delay=random.randint(args.delay[0], args.delay[1]))
    # with open('configuration.yaml', 'r') as file:
    #     data = yaml.safe_load(file)
    #
    # print(data)

if __name__ == '__main__':
    asyncio.run(startup())
