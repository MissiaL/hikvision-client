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


There are two formats for receiving a response:


**1. Dict(default):**


    .. code:: python

        from hikvision import Client

        api = Client('http://192.168.0.2', 'admin', 'admin')
        response = api.System.deviceInfo(method='get')

        response = {u'DeviceInfo': {u'@version': u'2.0',
                     u'@xmlns': u'http://www.hikvision.com/ver20/XMLSchema',
                     u'bootReleasedDate': u'100316',
                     u'bootVersion': u'V1.3.4',
                     '...':'...'
                   }


**2. Text**


    .. code:: python

        response = api.System.deviceInfo(method='get', present='text')

    .. code:: text

        response = '<?xml version="1.0" encoding="UTF-8" ?>
        <DeviceInfo version="1.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
        <deviceName>HIKVISION</deviceName>
        </DeviceInfo>'


Hints:
""""""


1. Channel info

    .. code:: python

        api.System.Video.inputs.channels[1].motionDetection(method='get')


2. Send data to device:

    .. code:: python

        xml = api.System.deviceInfo(method='get', present='text')
        api.System.deviceInfo(method='put', data=xml)

3. Get events(motion, etc..)
    .. code:: python

        client = Client('http://192.168.0.2', 'admin', 'Password')
        client.count_events = 2 # The number of events that need to(default = 1)
        response = client.Event.notification.alertStream(method='get')

        response = [{u'EventNotificationAlert':
                             {u'@version': u'2.0',
                              u'@xmlns': u'http://www.hikvision.com/ver20/XMLSchema',
                              u'activePostCount': u'0',
                              u'channelID': u'1',
                              u'dateTime': u'2018-03-21T15:49:02+08:00',
                              u'eventDescription': u'videoloss alarm',
                              u'eventState': u'inactive',
                              u'eventType': u'videoloss'
                             }
                   }]


