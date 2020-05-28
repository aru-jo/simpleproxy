import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.request import Request, urlopen

TABLE_ID = 'proxylisttable'


class Proxy(object):
    def __init__(self, repeat_random_proxy=2):
        self.url = 'https://www.sslproxies.org/'
        self.ua = UserAgent()
        self.proxy_list = []
        self.count = 0
        self.per_count_proxy = None
        self.repeat_random_proxy = repeat_random_proxy

    def get_proxy_sampling(self, k):
        """
        :return: non repeating list of ip and ports
        """
        return random.sample(self.proxy_list, k=k)

    def refresh_proxies(self):
        self.get_proxy_list_initial()

    def get_random_proxy(self):
        """
        :return: random proxy ip and port (int) from proxy list
        """
        if self.proxy_list:
            return self.proxy_list[random.randint(0, len(self.proxy_list) - 1)]
        else:
            print('Proxy List is not created yet - invoke get_proxy_list()')

    def get_sslproxies_html(self):
        """
        :return: beautiful soup object of sslproxies.org
        """
        proxies_req = Request(self.url)
        proxies_req.add_header('User-Agent', self.ua.random)
        sslproxies_html = urlopen(proxies_req).read().decode('utf8')
        soup = BeautifulSoup(sslproxies_html, 'html.parser')
        return soup

    def get_proxy_list(self):
        """
        :return: latest proxy list if already stored else calculate and return it.
        """
        if len(self.proxy_list):
            return self.proxy_list
        else:
            return self.get_proxy_list_initial()

    def get_proxy_list_initial(self):
        """
        :return: proxy list
        """
        soup_object = self.get_sslproxies_html()
        pr_table = self.get_table_using_id(soup_object)
        if pr_table:
            self.proxy_list = self.save_proxies(pr_table)
            if not self.proxy_list:
                print('Proxy list could not be generated due to error in save_proxies()')
        else:
            print('Table could not be retrieved, check sslproxies.org to find table id')
        return self.proxy_list

    @staticmethod
    def get_table_using_id(soup):
        """
        :param soup: soup_object
        :return: proxies table html
        """
        # using the id get the free proxy table list from sslproxies.org

        proxies_table = soup.find(id=TABLE_ID)
        if proxies_table:
            return proxies_table

    @staticmethod
    def save_proxies(proxies_table):
        """
        :param proxies_table:
        :return: proxies dictionary: Data store to contain proxies in the form [{'ip': ip_val, 'port':port_val},...]
        """
        proxies = []
        try:
            for row in proxies_table.tbody.find_all('tr'):
                proxies.append({
                    'ip': row.find_all('td')[0].string,
                    'port': row.find_all('td')[1].string
                })
        except AttributeError:
            return False
        return proxies

    def set_random_proxy_per_count(self, x):
        """
        :param x: set self.repeat_random_proxy to x where x is a positive integer.
        :return: None
        """
        if x > 0:
            self.repeat_random_proxy = x
        else:
            print('Repeat random proxy cannot be negative')

    def get_random_proxy_per_count(self):
        """
        :return: gives a random proxy ip, port pair for every (self.repeat_random_proxy) time calls.
        For example if self.repeat_random_proxy is 2 (default), get a random proxy every 2 calls to
        get_random_proxy_per_count. Set self.repeat_random_proxy in set_random_proxy_per_count
        """
        self.count += 1
        if self.per_count_proxy is None:
            self.per_count_proxy = self.get_random_proxy()
            return self.per_count_proxy
        try:
            if self.count % self.repeat_random_proxy == 0:
                self.per_count_proxy = self.get_random_proxy()
        except ZeroDivisionError:
            print('x cannot be 0')
        return self.per_count_proxy

        # TO-DO : add proxy server country and server status (active/inactive)
