import random
# import requests
# from bs4 import BeautifulSoup


def set_proxy(conf_data: dict) -> list:
    proxies = conf_data['proxies']

    random.shuffle(proxies)
    return proxies


# def function():
#     work = requests.Session()
#     url = 'https://panel.proxyline.net/login/'
#     response = work.get(url)
#     soup = BeautifulSoup(response.text, 'lxml')
#     token = soup.find('form').find('input').get('value')
#
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit\
#         605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15'
#     }
#
#     data = {'csrfmiddlewaretoken': token,
#             'email': '51203yarik@gmail.com',
#             'password': '1z7pikMpv1UKhTvuIuucA3s3Z'}
#
#     response = requests.post(url, data=data, headers=headers)
#
#
# def main():
#     function()
#
#
# if __name__ == '__main__':
#     main()
