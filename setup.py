from setuptools import setup
from setuptools import find_packages

setup(
      name='mwa_pulsar_client',
      version='0.1',
      description='Client interface to MWA Pulsar DB',
      author='Dave Pallot',
      author_email='dave.pallot@icrar.org',
      url='',
      packages=find_packages(),
      install_requires=[
        'requests'
      ],
)
