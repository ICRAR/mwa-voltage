from setuptools import setup
from setuptools import find_packages
from subprocess import check_output

#The following two functions were taken from the repo: https://github.com/pyfidelity/setuptools-git-version/blob/master/setuptools_git_version.py
def format_version(version, fmt='{tag}.{commitcount}'):
    parts = version.split('-')
    if len(parts) == 1:
        return parts[0]
    assert len(parts) in (3, 4)
    dirty = len(parts) == 4
    tag, count, sha = parts[:3]
    if count == '0' and not dirty:
        return tag
    return fmt.format(tag=tag, commitcount=count)

def get_git_version():
    git_version = check_output('git describe --tags --long --dirty --always'.split()).decode('utf-8').strip()
    return format_version(version=git_version)

setup(
      name='mwa-voltage',
      version=get_git_version(),
      description='Tools for processing MWA voltage data',
      author='Dave Pallot',
      author_email='dave.pallot@icrar.org',
      url='',
      packages=find_packages(),
      install_requires=['requests'],
      scripts=['scripts/voltdownload.py']
)
