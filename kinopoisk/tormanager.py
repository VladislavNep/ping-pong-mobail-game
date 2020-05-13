import time
import urllib.request
import urllib.error
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller


class ConnectionManager:

    def __init__(self, tor_password):
        self.new_ip = "0.0.0.0"
        self.old_ip = "0.0.0.0"
        self.tor_password = tor_password
        self.new_identity()

    def _get_connection(self):
        """
        TOR new connection
        """
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=self.tor_password)
            controller.signal(Signal.NEWNYM)
            controller.close()

    @classmethod
    def _set_url_proxy(cls):
        """
        Request to URL through local proxy
        """
        proxy_support = urllib.request.ProxyHandler({"http": "127.0.0.1:8118"})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

    @classmethod
    def request(cls, url):
        """
        TOR communication through local proxy
        :param url: web page to parser
        :return: request
        """
        try:
            cls._set_url_proxy()
            request = urllib.request.Request(url, None, {'User-Agent': UserAgent().random})
            request = urllib.request.urlopen(request)
            return request
        except urllib.error.HTTPError as e:
            return e

    def new_identity(self):
        """
        new connection with new IP
        """
        # First Connection
        if self.new_ip == "0.0.0.0":
            self._get_connection()
            self.new_ip = self.request("http://icanhazip.com/").read()
        else:
            self.old_ip = self.new_ip
            self._get_connection()
            self.new_ip = self.request("http://icanhazip.com/").read()

        seg = 0

        # If we get the same ip, we'll wait 5 seconds to request a new IP
        while self.old_ip == self.new_ip:
            time.sleep(5)
            seg += 5
            print("Waiting to obtain new IP: %s Seconds" % seg)
            self.new_ip = self.request("http://icanhazip.com/").read()

        print("New connection with IP: %s" % self.new_ip)
