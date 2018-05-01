from setuptools import setup, find_packages
from os.path import join, dirname
import re

with open('hikvisionapi/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(name='hikvisionapi',
      version=version,
      description='The client for HIKVISION cameras, DVR',
      url='https://github.com/MissiaL/hikvision-client',
      author='Petr Alekseev',
      author_email='petrmissial@gmail.com',
      packages=find_packages(),
      long_description=open(join(dirname(__file__), 'README.md')).read(),
      download_url='https://github.com/MissiaL/hikvision-client/tarball/{}'.format(version),
      keywords=['api', 'hikvision', 'hikvision-client'],
      install_requires=['xmltodict', 'requests']
      )
