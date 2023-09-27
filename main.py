import asyncio
import yaml

from loguru import logger
import collectors.launcher as launcher

logger.add('debug.log', format='{time} | {level} | {message}', level='DEBUG',
           rotation='20 mb', compression='zip')


async def startup():
    with open('configuration.yaml', 'r') as file:
        conf_data = yaml.safe_load(file)

    await launcher.loader(conf_data=conf_data)


if __name__ == '__main__':
    asyncio.run(startup())
