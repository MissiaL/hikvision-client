# coding=utf-8

import inspect
import json
from typing import Any, AsyncGenerator, AsyncIterator, Coroutine, List, Optional, Union
from urllib.parse import urljoin

import httpx
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import xmltodict


class ConvertToJsonError(Exception):
    pass


class DynamicMethod(object):
    def __init__(self, client, path):
        self.client = client
        self.path = path

    def __repr__(self):
        return f"<DynamicMethod client={self.client} path={self.path}"

    def __getattr__(self, key):
        return DynamicMethod(self.client, '/'.join((self.path, key)))

    def __getitem__(self, item):
        return DynamicMethod(self.client, self.path + "/" + str(item))

    def __call__(self, **kwargs):
        assert 'method' in kwargs, "set http method in args"
        return self.client.request(self.path, **kwargs)

async def async_response_parser(response, present='dict'):
    if inspect.iscoroutine(response):
        data = await response
    else:
        data = response
    return response_parser(data, present=present)


def response_parser(response, present='dict'):
    """ Convert Hikvision results
    """
    if isinstance(response, (list,)):
        result = "".join(response)
    elif isinstance(response, str):
        result = response
    else:
        result = response.text

    if present is None or present == 'dict':
        if isinstance(response, (list,)):
            events = []
            for event in response:
                e = json.loads(json.dumps(xmltodict.parse(event)))
                events.append(e)
            return events
        return json.loads(json.dumps(xmltodict.parse(result)))
    else:
        return result


class Client:
    """
    Client for Hikvision API

    Class uses the dynamic methods to work with api

    Basic Usage::

    from hikvisionapi import Client
    api = Client('http://192.168.0.2', 'admin', 'admin')
    response = api.System.deviceInfo(method='get')

    response = {
        "DeviceInfo": {
            "@version": "1.0",
            "@xmlns": "http://www.hikvision.com/ver20/XMLSchema",
            "deviceName": "HIKVISION"
        }
    }

    or as text

    response = api.System.deviceInfo(method='get', present='text)

    <?xml version="1.0" encoding="UTF-8" ?>
        <DeviceInfo version="1.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
        <deviceName>HIKVISION</deviceName>
    </DeviceInfo>
    """

    def __init__(self, host, login=None, password=None, timeout=3, isapi_prefix='ISAPI'):
        """
        :param host: Host for device ('http://192.168.0.2')
        :param login: (optional) Login for device
        :param password: (optional) Password for device
        :param isapi_prefix: (optional) defaults to ISAPI but can be customized
        :param timeout: (optional) Timeout for request
        """
        self.host = host
        self.login = login
        self.password = password
        self.timeout = float(timeout)
        self.isapi_prefix = isapi_prefix
        self.req = self._check_session()
        self.count_events = 1

    def _check_session(self):
        """Check the connection with device

         :return request.session() object
        """
        full_url = urljoin(self.host, self.isapi_prefix + '/System/status')
        session = requests.session()
        session.auth = HTTPBasicAuth(self.login, self.password)
        response = session.get(full_url)
        if response.status_code == 401:
            session.auth = HTTPDigestAuth(self.login, self.password)
            response = session.get(full_url)
        response.raise_for_status()
        return session

    def __getattr__(self, key):
        return DynamicMethod(self, key)

    def stream_request(self, method, full_url, **data):
        events = []
        response = self.req.request(method, full_url, timeout=self.timeout, stream=True, **data)
        for chunk in response.iter_lines(chunk_size=1024, delimiter=b'--boundary'):
            if chunk:
                xml = chunk.split(b'\r\n\r\n')[1].decode("utf-8")
                events.append(xml)
                if len(events) == self.count_events:
                    return events

    def opaque_request(self, method, full_url, **data):
        return self.req.request(method, full_url, timeout=self.timeout, stream=True, **data)

    def common_request(self, method, full_url, **data):
        response = self.req.request(method, full_url, timeout=self.timeout, **data)
        response.raise_for_status()
        return response

    def _prepared_request(self, *args, **kwargs):
        url_path = list(args)
        url_path.insert(0, self.isapi_prefix)
        full_url = urljoin(self.host, "/".join(url_path))
        method = kwargs['method']

        data = kwargs
        data.pop('present', None)
        data.pop('method')
        supported_types = {
            'stream': self.stream_request,
            'opaque_data': self.opaque_request
        }
        return_type = data.pop('type', '').lower()

        if return_type in supported_types and method == 'get':
            return supported_types[return_type](method, full_url, **data)
        else:
            return self.common_request(method, full_url, **data)

    def request(self, *args, **kwargs):
        response = self._prepared_request(*args, **kwargs)
        present = kwargs.get('present', 'dict')
        return_type = kwargs.get('type', '').lower()
        if return_type == 'opaque_data':
            return response
        return response_parser(response, present)


class AsyncClient:
    """
    Async Client for Hikvision API

    Class uses the dynamic methods to work with api

    Basic Usage::

    from hikvisionapi import AsyncClient
    api = AsyncClient('http://192.168.0.2', 'admin', 'admin')
    response = await api.System.deviceInfo(method='get')

    response = {
        "DeviceInfo": {
            "@version": "1.0",
            "@xmlns": "http://www.hikvision.com/ver20/XMLSchema",
            "deviceName": "HIKVISION"
        }
    }

    or as text

    response = api.System.deviceInfo(method='get', present='text)

    <?xml version="1.0" encoding="UTF-8" ?>
        <DeviceInfo version="1.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
        <deviceName>HIKVISION</deviceName>
    </DeviceInfo>
    """

    def __init__(
        self,
        host: str,
        login: str,
        password: str,
        timeout: Optional[float] = 3,
        isapi_prefix: str = "ISAPI",
    ):
        """
        :param host: Host for device ('http://192.168.0.2')
        :param login: (optional) Login for device
        :param password: (optional) Password for device
        :param isapi_prefix: (optional) defaults to ISAPI but can be customized
        :param timeout: (optional) Default timeout for requests
        """
        self.host: str = host
        self.login: str = login
        self.password: str = password
        self.timeout: Optional[float] = timeout
        self.isapi_prefix: str = isapi_prefix
        self._auth_method: Optional[httpx._auth.Auth] = None

    def __getattr__(self, key: str):
        return DynamicMethod(self, key)


    async def _detect_auth_method(self):
        """Establish the connection with device"""
        full_url = urljoin(self.host, self.isapi_prefix + '/System/status')
        for method in [
            httpx.BasicAuth(self.login, self.password),
            httpx.DigestAuth(self.login, self.password),
        ]:
                async with httpx.AsyncClient(auth=method) as client:
                    response = await client.get(full_url)
                    if response.status_code == 200:
                        self._auth_method = method

        if not self._auth_method:
            response.raise_for_status()

    async def stream_request(
        self,
        method: str,
        full_url: str,
        present: str,
        timeout: Optional[float],
        **data,
    ) -> AsyncGenerator[Union[List[str], str], None]:
        if not self._auth_method:
            await self._detect_auth_method()

        # This is a naive parser that assumes all stream endpoints will generate XML since
        # there aren't any convenient multipart readers
        async with httpx.AsyncClient(auth=self._auth_method) as client:
            async with client.stream(
                method, full_url, timeout=timeout, **data
            ) as response:
                buffer = ""
                opening_tag = None

                async for chunk in response.aiter_text():
                    buffer += chunk
                    events = buffer.split("\r\n\r\n")[1:]

                    if not opening_tag and len(events) > 0 and ">" in events[0]:
                        opening_tag = events[0].split(">", 1)[0].split("<", 1)[1].split(" ")[0]

                    if opening_tag and f"</{opening_tag}>" in events[0]:
                        yield await async_response_parser(events[0].split(f"</{opening_tag}>", 1)[0] + f"</{opening_tag}>", present=present)
                        opening_tag = None
                        buffer = "".join(events[1:])

    async def opaque_request(
        self,
        method: str,
        full_url: str,
        present: str,
        timeout: Optional[float],
        **data,
    ) -> AsyncIterator[bytes]:
        if not self._auth_method:
            await self._detect_auth_method()

        async with httpx.AsyncClient(auth=self._auth_method) as client:
            async with client.stream(
                method, full_url, timeout=timeout, **data
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    async def common_request(
        self,
        method: str,
        full_url: str,
        present: str,
        timeout: Optional[float],
        **data,
    ) -> Union[List[str], str]:
        if not self._auth_method:
            await self._detect_auth_method()

        async with httpx.AsyncClient(auth=self._auth_method) as client:
            response = await client.request(method, full_url, timeout=timeout, **data)
            response.raise_for_status()
            return await async_response_parser(response, present)

    def request(
        self, *args, **kwargs
    ) -> Union[
        Coroutine[Any, Any, Union[List[str], str]],
        AsyncIterator[bytes],
        AsyncGenerator[Union[List[str], str], None],
    ]:
        url_path = list(args)
        url_path.insert(0, self.isapi_prefix)
        full_url = urljoin(self.host, "/".join(url_path))

        method = kwargs["method"]
        kwargs.pop("method")
        present = kwargs.pop("present", None)
        supported_types = {
            'stream': self.stream_request,
            'opaque_data': self.opaque_request
        }
        return_type = kwargs.pop("type", "").lower()
        timeout = kwargs.get("timeout", self.timeout)
        kwargs.pop("timeout", None)

        if return_type in supported_types and method == "get":
            return supported_types[return_type](
                method, full_url, present, timeout, **kwargs
            )
        else:
            return self.common_request(method, full_url, present, timeout, **kwargs)
