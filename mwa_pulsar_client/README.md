# MWA Pulsar Client

Python API to interface to the MWA Pulsar Database. 

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
## PSRCAT

The Pulsar database provides an API to PSRCAT.

Access it through the HTTP API:

```python
def psrcat(addr, auth, pulsar)
```

Or via the [PSRCAT webform] (https://mwa-pawsey-volt01.pawsey.ivec.org/psrcat/). Note you must be logged in to access the page. The username password is the same as your normal login. 

To input a pulsars name click on HTML tab at the bottom of the page. 

## PSRCAT Example 

```python
from mwa_pulsar_client import client

SERVER = 'mwa-pawsey-volt01.pawsey.ivec.org'
AUTH = ('mwapulsar', 'PASS') # Replace with real password

try:
    results = client.psrcat(SERVER, AUTH, pulsar = 'J1935+161')
    for r in results.items():
        print r
except requests.exceptions.RequestException as e:
    print e.response.text
```

### Enums
```
observation_create(obstype): 1: Contiguous, 2: Picket Fence
pulsar_file_upload(filetype): 1: Archive, 2: Timeseries, 3: Diagnostics, 4: Calibration Solution
```

## Example

Create pulsar. 

```python
from mwa_pulsar_client import client

SERVER = 'mwa-pawsey-volt01.pawsey.ivec.org'
AUTH = ('mwapulsar', 'PASS') # Replace with real password

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
