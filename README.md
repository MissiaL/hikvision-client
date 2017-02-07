LIbrary for Hikvision Cameras
===================


Simple and easy to use library for working with video equipment companies Hikvision

----------

Install
-------------

```
pip install hikvisionapi
```

Example
-------------


```python
from hikvisionapi import client

api = Client('http://192.168.0.2', 'admin', 'admin')
response = api.System.deviceInfo(method='get', json=True)
```

```json
response = {
	"DeviceInfo": {
	"@version": "1.0", "@xmlns": "http://www.hikvision.com/ver20/XMLSchema", 
	"deviceName": "HIKVISION"
}
```
You can get responseras text:

```python
response = api.System.deviceInfo(method='get', json=False)
```

```
response = <?xml version="1.0" encoding="UTF-8" ?>
<DeviceInfo version="1.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
<deviceName>HIKVISION</deviceName>
</DeviceInfo>
```

More examples:

```python
xml = api.System.deviceInfo(method='get', json=False)
api.System.deviceInfo(method='put', data=xml, json=False)
```