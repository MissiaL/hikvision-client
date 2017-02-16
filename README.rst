LIbrary for Hikvision Cameras
=============================

Simple and easy to use library for working with video equipment
companies Hikvision

--------------

Install
-------

.. code:: bash

    pip install hikvisionapi


Examples
--------

.. code:: python

    from hikvision import Client

    api = Client('http://192.168.0.2', 'admin', 'admin')
    response = api.System.deviceInfo(method='get', present='json')

.. code:: json

    response = {
        "DeviceInfo": {
        "@version": "1.0", "@xmlns": "http://www.hikvision.com/ver20/XMLSchema",
        "deviceName": "HIKVISION"
    }

You can get response as text:

.. code:: python

    response = api.System.deviceInfo(method='get', present='text')

.. code:: text

    response = '<?xml version="1.0" encoding="UTF-8" ?>
    <DeviceInfo version="1.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
    <deviceName>HIKVISION</deviceName>
    </DeviceInfo>'

By default response as dict:

.. code:: python

    response = api.System.deviceInfo(method='get')

.. code:: python

    response = {'DeviceInfo': {'deviceName': 'HIKVISION'}}


===========
<ID> prefix
===========

For the numbering of channels using at:

.. code:: python

    api.System.Video.inputs.channels[1].motionDetection(method='get')

url path:

.. code:: text

    'System/Video/inputs/channels/1/motionDetection'


More examples:

.. code:: python

    xml = api.System.deviceInfo(method='get', present='text')
    api.System.deviceInfo(method='put', data=xml)
