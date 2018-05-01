import os

import vcr

import hikvisionapi

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

my_vcr = vcr.VCR(
    cassette_library_dir = os.path.join(THIS_FILE_DIR, 'fixtures', 'cassettes'),
    record_mode = 'once',
    match_on = ['uri', 'path'],
)

@my_vcr.use_cassette()
def test_auth_firmware_pre_v5_5():
    client = hikvisionapi.Client('http://192.168.1.116', 'admin', 'password')
    device_info = client.System.deviceinfo(method='get')
    assert device_info['DeviceInfo']['firmwareVersion'] == 'V5.4.5'

@my_vcr.use_cassette()
def test_auth_firmware_v5_5():
    client = hikvisionapi.Client('http://192.168.1.161', 'admin', 'password')
    device_info = client.System.deviceinfo(method='get')
    assert device_info['DeviceInfo']['firmwareVersion'] == 'V5.5.0'

# VCRpy does not work with in stream mode
# @my_vcr.use_cassette()
# def test_stream_request():
    # client = hikvisionapi.Client('http://192.168.1.116', 'admin', 'password')
    # client.count_events = 1
    # response = client.Event.notification.alertStream(method='get')


