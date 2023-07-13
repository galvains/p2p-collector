import random


def set_proxy(conf_data: dict) -> list:
    proxies = conf_data['proxies']

    random.shuffle(proxies)
    return proxies
