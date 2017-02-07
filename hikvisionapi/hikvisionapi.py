# coding=utf-8

import requests
from requests.auth import HTTPBasicAuth
import xmltodict
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import json

ISAPI = 'ISAPI'


class ConvertToJsonError(Exception):
    pass


class DynamicMethod(object):
    def __init__(self, client, method_name):
        self.client = client
        self.method_name = method_name

    def __getattr__(self, key):
        return DynamicMethod(self.client, '/'.join((self.method_name, key)))

    def __call__(self, **kwargs):
        assert 'method' in kwargs, "set http method in args"
        return self.client.request(self.method_name, **kwargs)


def response_xml_parser(response):
    """ Convert Hikvision XML to JSON
    """
    xml = response.text
    try:
        js = json.dumps(xmltodict.parse(xml))
    except:
        msg = 'Failed {} convert to json'.format(xml)
        raise ConvertToJsonError(msg)
    return js


class Client:
    """Client for Hikvision API

    Class uses the dynamic methods to work with api

    Basic Usage::

    from hikvisionapi import Client
    api = Client('http://192.168.0.2', 'admin', 'admin')
    response = api.System.deviceInfo(method='get', json=True)

    Response as json

    response = {
        "DeviceInfo": {
            "@version": "1.0",
            "@xmlns": "http://www.hikvision.com/ver20/XMLSchema",
            "deviceName": "HIKVISION"
        }
    }

    or as text

    response = api.System.deviceInfo(method='get', json=False)

    <?xml version="1.0" encoding="UTF-8" ?>
        <DeviceInfo version="1.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
        <deviceName>HIKVISION</deviceName>
    </DeviceInfo>
    """

    def __init__(self, host, login=None, password=None, timeout=3):
        """
        :param host: Host for device ('http://192.168.0.2')
        :param login: (optional) Login for device
        :param password: (optional) Password for device
        :param timeout: (optional) Timeout for request
        """
        self.host = host
        self.login = login
        self.password = password
        self.timeout = float(timeout)
        self.req = self._check_session()

    def _check_session(self):
        """Check the connection with device

         :return request.session() object
        """
        full_url = urljoin(self.host, ISAPI + '/System/status')
        session = requests.session()
        session.auth = HTTPBasicAuth(self.login, self.password)
        response = session.get(full_url)
        response.raise_for_status()
        return session

    def __getattr__(self, key):
        return DynamicMethod(self, key)

    def _prepared_request(self, *args, **kwargs):
        url_path = list(args)
        url_path.insert(0, ISAPI)
        full_url = urljoin(self.host, "/".join(url_path))
        method = kwargs['method']

        data = kwargs
        data.pop('json', None)
        data.pop('method')
        response = self.req.request(method, full_url, timeout=self.timeout, **data)
        response.raise_for_status()
        return response

    def request(self, *args, **kwargs):
        response = self._prepared_request(*args, **kwargs)
        need_json = True if 'json' not in kwargs else kwargs.get('json')

        if need_json:
            return response_xml_parser(response)
        return response.text

if __name__ == '__main__':
    api = Client('http://172.17.11.112', 'admin', 'Password')
    response = api.System.deviceInfo(method='get', json=False)
    print (response)