# MWA Pulsar Client

Python API to the MWA Pulsar Database. 

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
def detection_find_calibrator(addr, auth, **kwargs):
    """
    Find calibrators used in a detection from a particular observation.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
        detection_obsid: observation id of a detection
    """

def calibrator_create(addr, auth, **kwargs):
    """
    Create a new calibrator.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id of the calibrator.
        caltype: id of calibrator type
        notes: any notes regarding calibrator
    """

def calibrator_list(addr, auth):
    """
    Return a list of the all the calibrators in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """

def calibrator_get(addr, auth, **kwargs):
    """
    Get a specific calibrator.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id of the calibrator.
        caltype: id of calibrator type (check database for type id)
    """

def pulsar_list(addr, auth):
    """
    Return a list of the all the pulars in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """

def pulsar_get(addr, auth, **kwargs):
    """
    Return a specified pulsar from the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        name: name of pulsar.
    """

def pulsar_create(addr, auth, **kwargs):
    """
    Create a new pulsar. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        name: name of pulsar.
        ra: right ascension of pulsar. 
        dec: declination of pulsar. 
    Raises:
        Exception if pulsar already exists or there is an input error.
    """
def detection_list(addr, auth):
    """
    Return a list of the all the pulsar detection in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """

def detection_get(addr, auth, **kwargs):
    """
    Return a specified pulsar detection from the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id.
    """

def detection_update(addr, auth, **kwargs):
    """
    Update an extising detection. 
    observationid, pulsar and subband, coherent form a unique set per detection. 

    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id. 
        pulsar: name of pulsar (string). 
        subband: subband of detection.
        coherent: coherent data set (True), incoherent (False)
        observation_type: type of observation (1: Contiguous, 2: Picket Fence)
        calibrator: id of calibrator (or None).
        startcchan: start course channel (or None).
        stopcchan: stop course channel (or None). 
        flux: mJy (or None)
        flux_error: ±mJy (or None)
        width: ms (or None)
        width_error: ±ms (or None)
        scattering: s (or None)
        scattering_error: ±s (or None)
        dm: pc/cm³ (or None)
        dm_error: ±pc/cm³
        
    Raises:
        Exception if detection already exists or there is an input error.
    """

def detection_create(addr, auth, **kwargs):
    """
    Create a new detection. 
    observationid, pulsar and subband, coherent form a unique set per detection. 

    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id. 
        pulsar: name of pulsar (string). 
        subband: subband of detection.
        coherent: coherent data set (True), incoherent (False)
        observation_type: type of observation (1: Contiguous, 2: Picket Fence)
        calibrator: id of calibrator (or None).
        startcchan: start course channel (or None).
        stopcchan: stop course channel (or None). 
        flux: mJy (or None)
        flux_error: ±mJy (or None)
        width: ms (or None)
        width_error: ±ms (or None)
        scattering: s (or None)
        scattering_error: ±s (or None)
        dm: pc/cm³ (or None)
        dm_error: ±pc/cm³

    Raises:
        Exception if detection already exists or there is an input error.
    """

def detection_file_upload(addr, auth, **kwargs):
    """
    Upload a file against a detection.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id.
        pulsar: name of pulsar. 
        subband: subband of detection.
        coherent: coherent observation.
        filetype: (1: Archive, 2: Timeseries, 3: Diagnostics, 4: Calibration Solution, 5: Bestprof)
        filepath: full local path of the file to upload. 
    """

def detection_file_download(addr, auth, filename, outputpath):
    """
    Download a specific detection file. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id.
        filename: name of the file recorded in the database. 
        out_path: local path where to place file.
    Returns:
        full path of the downloaded file.
    Raises:
        Exception if there is a file error or file not found. 
    """

def calibrator_file_upload(addr, auth, **kwargs):
    """
    Upload a file against a calibrator.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id.
        caltype: (check database for id)
        filepath: full local path of the file to upload. 
    """
 
 def calibrator_file_download(addr, auth, filename, outputpath):
    """
    Download a specific calibration file. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        filename: name of the file recorded in the database. 
        out_path: local path where to place file.
    Returns:
        full path of the downloaded file.
    Raises:
        Exception if there is a file error or file not found. 
    """

def psrcat(addr, auth, pulsar):
    """
    Return the pulsar details from psrcat.

    Args:
        pulsar: name of the pulsar.
    Returns:
        psrcat details as a python dict.
    Exception:
        pulsar not found or bad input.
    """
```

To determine the funtion parameters bring up a python terminal and use the help function.

```python

from mwa_pulsar_client import client
help(client.detection_create)

```

## Example

```python
from mwa_pulsar_client import client

SERVER = 'https://mwa-pawsey-volt01.pawsey.ivec.org'
AUTH = ('mwapulsar', 'PASS') # Replace with real password

try:

    client.pulsar_create(SERVER, 
                         AUTH, 
                         name = 'J1111+1111', 
                         ra = '19:35:47.8259', 
                         dec = '+16:16:39.986')
    
    result = client.calibrator_create(SERVER,
                                      AUTH,
                                      observationid = 123456,
                                      caltype = 1) # Offringa
                                      
    # upload calibration solution to this calibrator               
    client.calibrator_file_upload(SERVER,
                                AUTH,
                                observationid=123456,
                                caltype=1,
                                filepath='./calsol.tar')

    # create a detection and link it to the calibrator above                 
    client.detection_create(SERVER, 
                            AUTH,
                            observationid = 1111111111, 
                            pulsar = 'J1111+1111',
                            subband = 145,
                            coherent = True,
                            observation_type = 1, # Contiguous
                            calibrator = result['id'], # get the id of calibrator
                            startcchan = 130, 
                            stopcchan = 140, 
                            flux = 80,
                            width = 0.03,
                            dm = 130)
    
    # Return the calibrator used for the detection (if it exists)
    result = client.detection_find_calibrator(SERVER, 
                                              AUTH,
                                              detection_obsid = 1111111111)
    # json result as python objects
    print (result)
    
    # Change the DM
    # Requires observationid, pulsar, subband and coherent set to identify a unique detection
    client.detection_update(SERVER,
                            AUTH,
                            observationid = 1111111111, 
                            pulsar = 'J1111+1111',
                            subband = 145,
                            coherent = True,
                            dm = 120)
    
    # upload a file associated to a detection
    client.detection_file_upload(SERVER,
                                AUTH,
                                observationid = 1111111111, 
                                pulsar = 'J1111+1111',
                                subband = 145,
                                coherent = True,
                                filetype = 1, # Archive
                                filepath='./filter.jpg')
    
    # download a file to a particular location
    client.detection_file_download(SERVER,
                                    AUTH,
                                    filename='filter.jpg',
                                    outputpath='/tmp/')

# use this exception to catch any errors
except requests.exceptions.RequestException as e:
    print e.response.text
