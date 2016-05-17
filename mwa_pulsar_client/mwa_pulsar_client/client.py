import os
import urllib
import requests

def pulsar_list(addr, auth):
    """
    Return a list of the all the pulars in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_list')
    r = requests.post(url = path, auth = auth)
    r.raise_for_status()
    return r.json()

def pulsar_get(addr, auth, name):
    """
    Return a specified pulsar from the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        name: name of pulsar.
    """
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_get')
    payload = {'name': name}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def pulsar_create(addr, auth, name, ra, dec):
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
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_create')
    payload = {'name': name, 'ra': ra, 'dec': dec}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def observation_list(addr, auth):
    """
    Return a list of the all the pulsar observations in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """
    path = 'https://{0}/{1}/'.format(addr, 'observation_list')
    r = requests.post(url = path, auth = auth)
    r.raise_for_status()
    return r.json()

def observation_get(addr, auth, obsid):
    """
    Return a specified pulsar observation from the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        obsid: observation id.
    """
    path = 'https://{0}/{1}/'.format(addr, 'observation_get')
    payload = {'observationid': obsid}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def observation_create(addr, auth, obsid, pulsar, subband, obstype,
                       startcchan = None, stopcchan = None, flux = None,
                       flux_error = None, width = None, width_error = None,
                       scattering = None, scattering_error = None,
                       dm = None, dm_error = None):
    """
    Create a new pulsar. 
    Obsid, pulsar and subband form a unique set per observation. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        obsid: observation id. 
        pulsar: name of pulsar. 
        subband: subband of observation.
        obstype: type of observation (1: Contiguous, 2: Picket Fence)
        startcchan: start course channel.
        stopcchan: stop course channel. 
        flux: mJy
        flux_error: +-mJy
        width: ms
        width_error: +-ms
        scattering: s
        scattering_error: +-s
        dm: pc/cm^3
        dm_error: +-pc/cm^3
        
    Raises:
        Exception if observation already exists or there is an input error.
    """
    path = 'https://{0}/{1}/'.format(addr, 'observation_create')
    payload = {'observationid': obsid, 'pulsar': pulsar, 'subband': subband,
                'observationtype': obstype, 'startcchan': startcchan, 'stopcchan': stopcchan,
                'flux': flux, 'flux_error': flux_error,
                'width': width, 'width_error': width_error,
                'scattering': scattering, 'scattering_error': scattering_error,
                'dm': dm, 'dm_error': dm_error}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def pulsar_file_upload(addr, auth, obsid, pulsar, subband, filetype, filepath):
    """
    Upload a file against an observation. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        obsid: observation id.
        pulsar: name of pulsar. 
        subband: subband of observation.
        filetype: (1: Archive, 2: Timeseries, 3: Diagnostics, 4: Calibration Solution)
        filepath: full local path of the file to upload. 
    """
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_file_upload')
    headers = {'obsid': obsid, 'pulsar': pulsar, 'subband': subband,
                'filetype': filetype}
    files = {'path': open(filepath, 'rb')}
    r = requests.post(url = path, auth = auth, files = files, headers = headers)
    r.raise_for_status()
    return r.json()

def pulsar_file_download(addr, auth, filename, output_path):
    """
    Download a specific pulsar file. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        obsid: observation id.
        filename: name of the file recorded in the database. 
        out_path: local path where to place file.
    Returns:
        full path of the downloaded file.
    Raises:
        Exception if there is a file error or file not found. 
    """
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_file_download')
    params = {'filename': filename}
    r = requests.get(url = path,
                        auth = auth,
                        params = urllib.urlencode(params),
                        stream = True)
    r.raise_for_status()

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    full_output_path = '{0}/{1}'.format(output_path, filename)
    with open(full_output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)

    return full_output_path


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
    path = 'https://{0}/{1}/'.format(addr, 'psrcat')
    payload = {'name': pulsar, 'format': 'json'}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()
