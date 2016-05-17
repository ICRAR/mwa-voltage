# MWA Pulsar Client

Python API to interface to the MWA Pulsar Dataabase. 

## Installation

1. Clone repository. 
2. Create virtual environment if necessary.
3. Install client.
```
git clone https://github.com/ICRAR/mwa-voltage
virtualenv client
source client/bin/activate
cd mwa-voltage/mwa_pulsar_client
python setup.py install
```
## Functions

```python
def pulsar_list(addr, auth)
def pulsar_get(addr, auth, name)
def pulsar_create(addr, auth, name, ra, dec)
def observation_list(addr, auth)
def observation_get(addr, auth, obsid)
def observation_create(addr, auth, obsid, pulsar, subband, obstype,
                       startcchan = None, stopcchan = None, flux = None,
                       flux_error = None, width = None, width_error = None,
                       scattering = None, scattering_error = None,
                       dm = None, dm_error = None)
def pulsar_file_upload(addr, auth, obsid, pulsar, subband, filetype, filepath)
def pulsar_file_download(addr, auth, filename, output_path)
```

## Example

Create pulsar. 

```python
from mwa_pulsar_client import client

client.pulsar_create(SERVER, AUTH, 
                     name = 'J1935+1615', 
                     ra = '19:35:47.8259', 
                     dec = '+16:16:39.986') 
```

Create pulsar observation. 

```python
client.observation_create(SERVER, AUTH, 
                          obsid = 1095506112, 
                          pulsar = 'J1935+1615',
                          subband = 145, 
                          obstype = 1, # Contiguous
                          startcchan = 130, 
                          stopcchan = 140, 
                          flux = 80,
                          width = 0.03,
                          dm = 130)
```

Upload a pulsar observation file. 

```python
client.pulsar_file_upload(SERVER, AUTH, 
                          obsid = 1095506112, 
                          pulsar = 'J1935+1615',
                          subband = 145,
                          filetype = 1, # Archive file
                          filepath = '/tmp/test.ar')
```

List all the observations with a particular observation ID.

```python
observations = client.observation_get(SERVER, AUTH, obsid = 1095506112)
for observation in observations:
    print observation
```

Download file.

```python
client.pulsar_file_download(SERVER, AUTH, 'test.ar', '/tmp/downloads/')
```
